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
	int chosen_file;
	int f:1;
};

struct input_files listfiles(){
	DIR *d;
	struct dirent *dir;
	struct input_files captures;
	char directory[] = "./captures";
	//allocate memory for MAX_FILENUM amount of char pointers.
	captures.files = malloc(MAX_FILENUM*sizeof(char*));
	for(int i=0;i<MAX_FILENUM;i++){
		//allocate memory for MAX_FILELEN characters in a filename.
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

struct input_files getfile(struct input_files captures){
	printf("Please enter the number of the file you wish to read: ");
	char input[MAX_FILELEN];
	fgets(input,MAX_FILELEN,stdin);
	int val = atoi(input);
	captures.chosen_file = val;
	//printf("\nNumber you chose: %d\nAffiliated File: %s\n",val,captures.files[val-1]);
	//printf("Number of captures: %d\n",captures.num_files);
	return captures;
}

char* concat(const char *s1, const char *s2)
{
    char *result = malloc(strlen(s1) + strlen(s2) + 1); // +1 for the null-terminator
    // in real code you would check for errors in malloc here
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}

char* itoa(u_int8_t val, u_int8_t base){
	static char buf[32] = {0};
	u_int8_t i = 30;
	for(; val && i ; --i, val /= base)
		buf[i] = "0123456789abcdef"[val % base];
	return &buf[i+1];
}

void decode(struct input_files captures){
	FILE *fm_file;
	FILE *temp_file;
	char *file_name = concat("captures/",captures.files[captures.chosen_file-1]);
	printf("filename: %s\n",file_name);
	fm_file = fopen(file_name, "rb");
	u_int8_t buff[2];
	
	//clear the file before appending
	temp_file = fopen("temp.csv","w");
	fclose(temp_file);
	temp_file = fopen("temp.csv", "a");
	//fread: location in memory, size in bytes of elements, number of elements to read, file to read from.
	int counter = 1;
	while(fread(&buff,1,2,fm_file) && counter < 10){
		float inphase = buff[0]-127.5;
		float quadrature = buff[1]-127.5;
		
		
		//write to CSV file
		char *firstbyte = itoa(buff[0],10);
		//the below commented code does the same thing as itoa function.
		//char buffer[8];
		//snprintf(buffer, 6, "%d", buff[0]); 
		printf("The first byte: %f and %s\n",inphase,firstbyte);
		fputs(firstbyte,temp_file);
		fputs(",",temp_file);
		char *secondbyte = itoa(buff[1],10);
		printf("The second byte: %d and %s\n",buff[1],secondbyte);
		fputs(secondbyte,temp_file);
		fputs("\n",temp_file);
		counter++;
	}
	fclose(temp_file);
	fclose(fm_file);
}


int main(){
	struct input_files captures = listfiles();
	if(captures.f == 0){
		captures = getfile(captures);
		printf("Now decoding %s...\n",captures.files[captures.chosen_file-1]);
		decode(captures);
	}
	else{
		printf("exiting...\n");
	}
}
