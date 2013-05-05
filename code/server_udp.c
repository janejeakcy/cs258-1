#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <semaphore.h>
#include "mongoose.h"
#include "udp_client.h"

/*
   CS258 project
   Mongoose server, update balance to POX controller
   Xiaohan Li
   Apr. 11, 2013
 */

//global defination
int balance = 0;
int total_balance = 0;
struct socket_h *udp_h;
char buffer[150];
int namelen;
sem_t mutex;
FILE *CurrentLoadFile1;
FILE *CurrentLoadFile2;
FILE *CurrentTotalLoadFile;
char CurrentLoadFileName1[150];
char CurrentLoadFileName2[150];
char CurrentTotalLoadFileName[150];
pthread_t thread;

void senddata(struct socket_h *hp, int balance)
{
    int rv = 0;
    int retry = 1;
    buffer[namelen] = ':';
    while(retry <= 20)
    {
        memset(buffer + namelen + 1, 0, 20);
	    sprintf(buffer + namelen + 1, "%d\0", balance);
	    printf("about to send:%s\n", buffer);
	    if(udp_send(hp, buffer) >= 0)
            break;
        retry ++;
    }
}

void print_request_info(struct mg_connection *conn) {
	const struct mg_request_info *ri = mg_get_request_info(conn);
	printf("Remote IP: [%ld]\n", ri->remote_ip);
	printf("Remote port: [%d]\n", ri->remote_port);
}

int begin_request_handler(struct mg_connection *conn) {
	print_request_info(conn);
    total_balance ++;
    //fprintf(CurrentTotalLoadFile, "total balance = %d\r\n", total_balance);
	sem_wait(&mutex);
    balance ++;
    fprintf(CurrentLoadFile1, "balance = %d\r\n", balance);
    sem_post(&mutex);
	printf("blance = [%d]\n", balance);
	senddata(udp_h, balance);
	return 0;
}

void end_request_handler(struct mg_connection *conn, int status_code){
	print_request_info(conn);
	sem_wait(&mutex);
    balance --;
    fprintf(CurrentLoadFile1, "balance = %d\r\n", balance);
    sem_post(&mutex);
	printf("blance = [%d]\n", balance);
	senddata(udp_h, balance);
}

void *write_load_info()
{
    while (CurrentLoadFile2 != NULL && CurrentTotalLoadFile != NULL)
    {
        fprintf(CurrentLoadFile2, "%d\r\n", balance);
        fprintf(CurrentTotalLoadFile, "%d\r\n", total_balance);
        usleep(500000);
    }
    pthread_exit(NULL);
}

int main(int argc, char** argv) {
	struct mg_context *ctx;
	struct mg_callbacks callbacks;
    int i;
    int temp;

	const char *options[] = {"listening_ports", "8080", NULL};

    sprintf(CurrentLoadFileName1, "c%s_rr_3.txt", argv[1]);
    sprintf(CurrentLoadFileName2, "s%s_rr_3.txt", argv[1]);
    sprintf(CurrentTotalLoadFileName, "t%s_rr_3.txt", argv[1]);
    CurrentLoadFile1 = fopen(CurrentLoadFileName1, "w");
    CurrentLoadFile2 = fopen(CurrentLoadFileName2, "w");
    CurrentTotalLoadFile = fopen(CurrentTotalLoadFileName, "w");

    sem_init(&mutex, 0, 1);    

	if(argc < 3){
	    printf("%s(servername, POX IP)\n", argv[0]);
		return 0;
	}
	
	printf("name = %s, POX=%s\n", argv[1], argv[2]);
	memset(&callbacks, 0, sizeof(callbacks));
	callbacks.begin_request = &begin_request_handler;
	callbacks.end_request = &end_request_handler;

	//Init the socket handle
	memset(buffer, 0x00, sizeof(buffer));
	namelen = strlen(argv[1]);
	strcpy(buffer, argv[1]);
	udp_h = udp_init(argv[2]);

	// Start the web server.
	ctx = mg_start(&callbacks, NULL, options);

    if ((temp = pthread_create(&thread, NULL, write_load_info, NULL) != 0))
        printf("thread fails\n");    

	// Wait until user hits "enter". Server is running in separate thread.
	// Navigating to http://localhost:8080 will invoke begin_request_handler().
    while (1)
    {
        i++;
    }

	// Stop the server.
	mg_stop(ctx);

	//close the udp handle
	udp_close(udp_h);
    sem_destroy(&mutex);
    fclose(CurrentLoadFile1);
    fclose(CurrentLoadFile2);
    fclose(CurrentTotalLoadFile);
	return 0;
}
