#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
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
struct socket_h *udp_h;
char buffer[150];
int namelen;

void senddata(struct socket_h *hp, int balance)
{
	buffer[namelen] = ':';
	sprintf(buffer + namelen + 1, "%d\0", balance);
	printf("about to send:%s\n", buffer);
	udp_send(hp, buffer);
}

void print_request_info(struct mg_connection *conn) {
	const struct mg_request_info *ri = mg_get_request_info(conn);
	printf("Remote IP: [%ld]\n", ri->remote_ip);
	printf("Remote port: [%d]\n", ri->remote_port);
}

int begin_request_handler(struct mg_connection *conn) {
	print_request_info(conn);
	balance ++;
	printf("blance = [%d]\n", balance);
	senddata(udp_h, balance);
	return 0;
}

void end_request_handler(struct mg_connection *conn, int status_code){
	print_request_info(conn);
	balance --;
	printf("blance = [%d]\n", balance);
	senddata(udp_h, balance);
}

int main(int argc, char** argv) {
	struct mg_context *ctx;
	struct mg_callbacks callbacks;
    int i;

	const char *options[] = {"listening_ports", "8080", NULL};

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

	return 0;
}
