#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <errno.h>
#include <string.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>   
#include <sys/socket.h> 
#include <time.h>
#include <stdarg.h>
#include "udp_client.h"

/*
 * CS258 project
 * Xiaohan Li
 * March 27, 2013
 */

struct socket_h
{
    int sock_id, timeout;
    struct sockaddr_in sa, ca;
    char *buffer;
};

void error(struct socket_h *ph,  const char * format, ... )
{
   //clean up
   udp_close(ph);

   //print
	va_list args;
	va_start(args, format);
	vprintf(format, args);
	va_end(args);
	//exit
	exit(-1);
}


struct socket_h *udp_init(char* addr)
{
   
    struct socket_h *ph;
	int tmp;
	struct timeval tv_timeout;
    struct hostent *hptr;//owned by system 
	
    //Init
	ph = (struct socket_h *)malloc(sizeof(struct socket_h));
    ph->timeout = 1000;
    ph->buffer = NULL;
	ph->buffer = (char*)malloc(151);
	if(ph->buffer == NULL)
	    error(ph, "not enouth memory\n");	
    memset(ph->buffer, 0x00, 151);
 
    //Create socket by using UDP
    ph->sock_id = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if(-1 == ph->sock_id)
         error(ph, "Can't Create Socket\n");
 
    //set timeout
    tmp = ph->timeout / 1000; 
    tv_timeout.tv_sec = tmp;
    tv_timeout.tv_usec = (ph->timeout%1000)*1000;
    if (setsockopt(ph->sock_id, SOL_SOCKET, SO_RCVTIMEO,
           (char*)&tv_timeout,sizeof(tv_timeout)) < 0) 
         error(ph, "Error in set timeout\n");
 
	//verify the address
	if ((hptr = gethostbyname(addr)) == NULL)   
         error(ph, "%s is not a correct host name \n", addr);   

    //Init server address
    memset(&(ph->sa), 0, sizeof(ph->sa));
    ph->sa.sin_family = AF_INET;
    ph->sa.sin_port = htons(9930);
    //bcopy( hptr->h_addr, &(ph->sa.sin_addr.s_addr), hptr->h_length);
    memcpy(&(ph->sa.sin_addr.s_addr), hptr->h_addr, hptr->h_length);

    //Init client address
    memset(&(ph->ca), 0, sizeof (ph->ca));
    ph->ca.sin_family = AF_INET;
    ph->ca.sin_addr.s_addr = htonl(INADDR_ANY); //any address
    ph->ca.sin_port = htons(0); //any port

    //Bind (to receive echo data)
    if(-1 == bind(ph->sock_id, (struct sockaddr *) &(ph->ca), sizeof(ph->ca)))
        error(ph, "Can't Bind Socket\n");
	
	return ph;
}

int udp_send(struct socket_h *ph, char* text)
{
    int size;
	int bytes_sent, bytes_receive;

	size = strlen(text);
	if(size <= 0 || size > 150)
	    error(ph, "data should be 0 - 150 bytes\n");

    //Send data
	bytes_sent = sendto(ph->sock_id, text, size, 0,(struct sockaddr*)&(ph->sa), sizeof(ph->sa));
	if (bytes_sent < 0) 
		error(ph, "Error for Sending the Packet: %s\n", strerror(errno));
	//Get response from server
	bytes_receive = recvfrom(ph->sock_id, (void *)(ph->buffer), size, 0, NULL, 0);
	if(bytes_receive != size)
    {
		//error(ph, "Warrning: packet lost: %s\n", strerror(errno));
        printf("Warrning: packet lost: %s\n", strerror(errno));
        return -1;
    }
    return 0;
}


void udp_close(struct socket_h *ph)
{
    //clear up socket_h
    if(NULL != ph)
	{
	    if(-1 != ph->sock_id)
	        close(ph->sock_id);
		
		if(NULL != ph->buffer)
		    free(ph->buffer);
	    
		free(ph);
	}
}

