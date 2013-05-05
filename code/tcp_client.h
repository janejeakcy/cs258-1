/*
CS258 project
tcp_client.h
functions for TCP communications using C programming language
*/

struct socket_tcp_h;
struct socket_tcp_h *tcp_init(char* addr);
int tcp_send(struct socket_tcp_h *ph, char* text);
void tcp_close(struct socket_tcp_h *ph);
