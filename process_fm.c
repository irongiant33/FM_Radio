#include <sys/types.h> //readdir,opendir
#include <dirent.h> //readdir,opendir
#include <stdio.h> //printf
#include <string.h> //strlen
#include <stdlib.h> //malloc, atoi

#define MAX_FILELEN 30
#define MAX_FILENUM 10

struct input_files{
	char **files;
	int num_files;
	int f:1;
};

struct input_files listfiles(){
	DIR *d;
	struct dirent *dir;
	struct input_files captures;
	char directory[] = "./captures";
	captures.files = malloc(MAX_FILENUM*sizeof(char*));
	for(int i=0;i<10;i++){
		captures.files[i] = malloc(MAX_FILELEN*sizeof(char));
	}
	
	d = opendir(directory);
	if(d){
		int count = 1;
		while((dir = readdir(d)) != NULL && count <= MAX_FILENUM){
			if(strlen(dir->d_name)>2 && strlen(dir->d_name) < MAX_FILELEN){
				printf("%d. %s\n",count,dir->d_name);
				captures.files[count-1] = dir->d_name;
				for(int i=0;i<strlen(dir->d_name);i++){
					captures.files[count-1][i]=dir->d_name[i];
				}
				count++;
			}
		}
		closedir(d);
		captures.num_files = count-1;
		return captures;
	}
	else{
		printf("Directory does not exist.\n");
		captures.f = 1;
		return captures;
	}
}

void getfile(struct input_files captures){
	printf("Please enter the number of the file you wish to read: ");
	char input[MAX_FILELEN];
	fgets(input,MAX_FILELEN,stdin);
	int val = atoi(input);
	printf("\nNumber you chose: %d\nAffiliated File: %s\n",val,captures.files[val-1]);
	printf("Number of captures: %d\n",captures.num_files);
}


int main(){
	struct input_files captures = listfiles();
	if(captures.f == 0){
		getfile(captures);
	}
	else{
		printf("exiting...\n");
	}
}
