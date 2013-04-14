/*
CS258 project
udp_client.h
functions for UDP communications using C programming language
*/
struct socket_h;
struct socket_h *udp_init(char* addr);
int udp_send(struct socket_h *ph, char* text);
void udp_close(struct socket_h *ph);

