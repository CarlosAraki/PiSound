#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include "include/csound/csound.h"

//Resolucao da camera
const int FRAME_WIDTH = 640;
const int FRAME_HEIGHT = 420;
//Volume mestre de saida (0 min, 1 max)
float MASTER_VOLUME = 1;
//Nome da FIFO
const char fifoName[] = "imgProcessFifo";

/* Estrutura para representar objeto capturado pela camera */
typedef struct {
    int state;  //Estado (0 - Desligado, 1 - Ligado)
    int x;      //Coord. x
    int y;      //Coord. y
}CameraObject;

/* Estrutura para os instrumentos 
 * A variavel activated indica se este instrumento esta habilitado para
 * sintetizacao. A variavel state indica se um instrumento ativado esta
 * sendo tocado neste momento ou nao.
 * A array de ponteiros chnPointers sera preenchida por ponteiros
 * para comunicacao com CSound. As posicoes comunicam:
 * 0 - Estado
 * 1 - Tipo
 * 2 - Frequencia
 * 3 - Amplitude */
const char* const instrumentChannels[] = {"State", "Type", "Freq", "Ampl"};
typedef struct {
    int number;                 //Numero do instrumento
    int activated;              //0 - Desativado, 1 - Ativado
    int state;                  //Estado(0 - Desligado, 1 - Ligado)
    int type;                   //Tipo (0 - seno comum)
    int frequency;              //Frequencia
    int frequencyRange[2];      //Faixa de possiveis frequencias
    int amplitude;              //Amplitude
    int amplitudeRange[2];      //Faixa de possiveis amplitudes
    float masterVolume;         //Volume mestre do instrumento
    int numOfChannels;    //Numero de canais de comunicacao
    MYFLT* chnPointers[4];      //Ponteiros para comunicacao com CSound 
}Instrument;

/* Estrutura para uso da API do CSound */
typedef struct {
    int result;         //Resultado da chamada csoundCompile()
    CSOUND *csound;     //Instancia do CSound
    int PERF_STATUS;    //Status da perfomance
}UserData;

//Funcoes para configuracao dos instrumentos
void getConfig();
void printConfig();
//Funcao executada pela thread que executara o CSound
uintptr_t perfomanceThread(void* clientData);
//Funcoes relacionadas aos instrumentos
void instrumentInitialize(Instrument* instr);
void instrumentGetPointers(Instrument* instr, UserData* ud);
void instrumentWriteToCSound(Instrument instr);

int main(int argc, char** argv) {
    CameraObject obj1, obj2;        //Objetos capturados pela camera
    int imgProcessPID;              //ID da thread que executara o processamento de imagem
    Instrument instr1, instr2;      //Instrumentos
    void *csoundThreadID;           //ID da thread que executara o CSound
    UserData *ud;                   //Estrutura para usar API Csound
    //Variaveis para fifo e syscall select
    int fifoFD;                     //File descriptor da FIFO
    char readBuffer[32];            //Buffer para leitura da FIFO
    fd_set fdset;                   //Conjunto de FDs
    struct timeval timeout;         //Tempo de timeout do select
    int retSelect;                  //Retorno do select

    //Inicializa instrumentos
    instrumentInitialize(&instr1);  
    instrumentInitialize(&instr2);

    //Obtem configuracao e imprime
    //getConfig();
    //printConfig();

    //Cria FIFO
    if(mkfifo(fifoName, 0600)) {
        if(errno == EEXIST) {
            printf("Erro ao criar pipe - pipe ja existe! Continuando normalmente.\n");
        } else {
            printf("Erro ao criar pipe - terminando aplicacao.\n");
            exit(1);
        }
    }

    /* Inicializacao da thread que processa imagem da webcam */
    //TODO ISSO

    /* Inicializacao do CSound */
    //Inicializa objeto CSOUND e compila arquivo csd.
    ud = (UserData*)malloc(sizeof(UserData));
    ud->csound = csoundCreate(NULL);                    
    ud->result = csoundCompile(ud->csound, argc, argv); 

    //Obtem ponteiros para comunicacao com o Csound
    instrumentGetPointers(&instr1, ud);
    instrumentGetPointers(&instr2, ud);

    //Caso a compilacao ocorreu com sucesso, cria um novo thread para rodar a aplicacao
    if(!ud->result) {
        ud->PERF_STATUS = 1;
        csoundThreadID = csoundCreateThread(perfomanceThread, (void*)ud);
    } else {
        printf("Falha ao compilar arquivo csound\n");
        exit(1);
    }
    
    /* Loop Principal */

    //Abre a FIFO
    fifoFD = open(fifoName, O_RDONLY);
    if(fifoFD == -1) {
        printf("Erro na abertura da FIFO!");
        //Limpar e terminar
    }
    while(inputFrequency != 0) {
        //Coloca a stdin e a fifo no set de fds monitorados pelo select
        FD_ZERO(&fdset);
        FD_SET(0, &fdset);
        FD_SET(fifoFD, &fdset);
        //Configura timeout
        timeout.tv_sec = 5;
        timeout.tv_usec = 0;
        //Monitora stdin e fifo
        retSelect = select(fifoFD+1, &fdset, NULL, NULL, &timeout);
        
        //Caso ocorra erro no select
        if(retSelect == -1) {
            printf("Erro no chamada select!");
        }

        //Caso algum FD esteja pronto para leitura
        else if (retSelect) {

            //Caso seja stdin, processa o comando
            if(FD_ISSET(0, &rfds)) {
                //Processa comando
            }

            //Caso seja a fifo, lê e atualiza instrumentos
            if(FD_ISSET(fifoFD, &rfds)) {
                if(read(fifoFD, readBuffer, 24) != 24) {
                    printf("Dados incompletos lidos na FIFO!\n");
                    //Lidar com isso?
                } else {
                    camObjUpdate(&obj1, &obj2, readBuffer);
                    instrumentUpdate(&instr1, &obj1);
                    instrumentUpdate(&instr2, &obj2);
                    instrumentWriteToCsound(instr1);
                    instrumentWriteToCsound(instr2);
                }
            }
        }
    }

    //Finaliza o programa
    ud->PERF_STATUS = 0;
    csoundDestroy(ud->csound);
    free(ud);

    return 0;

}

uintptr_t perfomanceThread(void *data) {
    UserData* udata = (UserData*)data;
    if(!udata->result) {
        while((csoundPerformKsmps(udata->csound) == 0 && (udata->PERF_STATUS == 1)));
        csoundDestroy(udata->csound);                                                                                                
    }
    udata->PERF_STATUS = 0;
    return 1;
}


/**************************************
* FUNCOES RELACIONADAS AOS CAMOBJECTS *
***************************************/

/* Obtem da array de bytes crus (se tudo estiver certo, 24 bytes)
 * os valores atualizados para as posicoes e estados dos objetos */
void camObjUpdate(CamObj* obj1, CamObj* obj2, char* bytes) {
    //TODO: arrumar essa merda
    obj1->x = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    obj1->y = (bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7];
    obj1->state = (bytes[8] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[8];
    obj2->x = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    obj2->y = (bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7];
    obj2->state = (bytes[8] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[8];

}

/****************************************
* FUNCOES RELACIONADAS AOS INSTRUMENTOS *
*****************************************/

/* Inicializa um novo instrumento na configuracao padrao */
void instrumentInitialize(Instrument* instr) {
    static int instrNumber = 1;
    instr->number = instrNumber;
    instr->activated = 0;
    instr->type = 0;
    instr->frequencyRange[0] = 440;
    instr->frequencyRange[1] = 7040;
    instr->amplitudeRange[0] = 0;
    instr->amplitudeRange[1] = 30000;
    instr->masterVolume = 1;
    instr->numOfChannels = sizeof(instrumentChannels)/sizeof(*instrumentChannels);
    instrNumber++;
}

void instrumentUpdate(Instrument* instr, CamObject* obj) {
    instr->state = obj->state;
    instr->frequency = (instr->frequencyRange[1]-instr->frequencyRange[0])*(FRAME_WIDTH/obj->x);
    instr->amplitude = (instr->amplitudeRange[1]-instr->amplitudeRange[0])*(FRAME_HEIGHT/obj->y)*(instr->masterVolume)*MASTER_VOLUME;
}

/* Obtem ponteiros para comunicacao com CSound e os armazena
 * nos ponteiros tipo *MYFLT da estrutura instrumento */
void instrumentGetPointers(Instrument* instr, UserData* ud) {
    char instrName[16];
    char channelName[32];
    char instrNumber;
    int i;

    //Obtem nome do instrumento (instr+numero)
    instrNumber = instr->number + '0';
    strcpy(instrName, "instr");
    strncat(instrName, &instrNumber, 1);

    //Obtem ponteiros para cada canal
    for(i=0; i<instr->numOfChannels; i++) {
        strcpy(channelName, instrName);
        strcat(channelName, instrumentChannels[i]);
        if(csoundGetChannelPtr(ud->csound, &(instr->chnPointers[i]), channelName, CSOUND_INPUT_CHANNEL | CSOUND_CONTROL_CHANNEL) != 0) {
            printf("Falha ao obter ponteiro para canal %s.\n", channelName);
            //TODO: Fazer cleanup antes do exit
            exit(1);
        }
    }
}

/* Escreve o estado, tipo, frequencia e amplitude do instrumento
 * nos respectivos ponteiros de comunicacao obtidos a partir de
 * getInstrumentPointers.
 * NAO use se nao tiver inicializado os ponteiros com sucesso! */
void instrumentWriteToCSound(Instrument instr) {
    *(instr.chnPointers[0]) = (MYFLT)instr.state;
    *(instr.chnPointers[1]) = (MYFLT)instr.type;
    *(instr.chnPointers[2]) = (MYFLT)instr.frequency;
    *(instr.chnPointers[3]) = (MYFLT)instr.amplitude;
}



                                            
