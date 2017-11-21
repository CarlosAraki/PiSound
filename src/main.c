#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <python2.7/Python.h>
#include "include/csound/csound.h"
#include "y.tab.h"


/* Estrutura para representar objeto capturado pela camera */
typedef struct {
    int number; //Numero do cameraObject
    int state;  //Estado (0 - Desligado, 1 - Ligado)
    float x;    //Coord. x
    float y;    //Coord. y
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
    float frequency;            //Frequencia
    float frequencyRange[2];    //Faixa de possiveis frequencias
    float amplitude;            //Amplitude
    float amplitudeRange[2];    //Faixa de possiveis amplitudes
    float masterVolume;         //Volume mestre do instrumento
    int numOfChannels;          //Numero de canais de comunicacao
    MYFLT* chnPointers[4];      //Ponteiros para comunicacao com CSound 
}Instrument;

/* Estrutura para uso da API do CSound */
typedef struct {
    int result;         //Resultado da chamada csoundCompile()
    CSOUND *csound;     //Instancia do CSound
    int PERF_STATUS;    //Status da perfomance
}UserData;

//Resolucao da camera
const float FRAME_WIDTH = 160;
const float FRAME_HEIGHT = 120;
//CameraObjects e instrumentos
CameraObject obj1, obj2;        //Objetos capturados pela camera
Instrument instr1, instr2;      //Instrumentos
//Volume mestre de saida (0 min, 1 max)
float MASTER_VOLUME = 1;
//Nome da FIFO
const char fifoName[] = "imgProcessFifo";

//Funcao executada pela thread que executara o script Python
void* imgProcessingThread(void *arg);
//Funcao executada pela thread que executara o CSound
uintptr_t perfomanceThread(void* clientData);
//Funcoes relacionados aos CameraObjects
void camObjInitialize(CameraObject* obj);
void camObjUpdate(CameraObject* obj1, CameraObject* obj2, char* bytes); 
void camObjPrint(CameraObject obj);
//Funcoes relacionadas aos instrumentos
void instrumentInitialize(Instrument* instr);
void instrumentUpdate(Instrument* instr, CameraObject* obj); 
void instrumentGetPointers(Instrument* instr, UserData* ud);
void instrumentWriteToCSound(Instrument instr);
void instrumentPrint(Instrument instr);

//Tratamento de comandos
void handleSetInstrPFF(char* instr, char* param, float val1, float val2);
void handleSetInstrPF(char* instr, char* param, float val);
void handleSetPF(char* param, float val);
void handlePrintP(char* param);
void handlePrintInstr(char* instr);
void handlePrintInstrP(char* instr, char* param);
void handlePrintCamobj(char* camobj);
void handlePrintCamobjP(char* camobj, char* param);
void handleHelp();
void handleExit();

int main(int argc, char** argv) {

    //Objetos de camera, instrumentos, variaveis para o CSound
    void *csoundThreadID;           //ID da thread que executara o CSound
    UserData *ud;                   //Estrutura para usar API Csound

    //Variaveis para fifo e syscall select
    int fifoFD;                     //File descriptor da FIFO
    char readBuffer[32];            //Buffer para leitura da FIFO
    fd_set fdset;                   //Conjunto de FDs
    struct timeval timeout;         //Tempo de timeout do select
    int retSelect;                  //Retorno do select

    pthread_t imgProcessThreadId;   //Id da thread de processamento de imagem
    int imgProcessThreadErr;        //Variavel de erro da criacao de threads

    //Inicializa instrumentos
    instrumentInitialize(&instr1);  
    instrumentInitialize(&instr2);
    //Inicializa CameraObjects
    camObjInitialize(&obj1);
    camObjInitialize(&obj2);

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
    imgProcessThreadErr = pthread_create(&imgProcessThreadId, NULL, &imgProcessingThread, NULL);
    if(imgProcessThreadErr != 0) {
        //TODO CLEANUP
        printf("Criacao da thread de processamento de imagem falhou!\n");
        exit(1);
    } else {
        printf("Thread de processamento de imagem criadacom sucesso!\n");
    }

    //sleep(100);
    /* Inicializacao do CSound */
    //Inicializa objeto CSOUND e compila arquivo csd.
    ud = (UserData*)malloc(sizeof(UserData));
    ud->csound = csoundCreate(NULL);                    
    ud->result = csoundCompile(ud->csound, argc, argv); 

    //Obtem ponteiros para comunicacao com o Csound
    instrumentGetPointers(&instr1, ud);
    //instrumentGetPointers(&instr2, ud);

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
    int bytes;
    readBuffer[16] = '\0';
    if(fifoFD == -1) {
        printf("Erro na abertura da FIFO!\n");
        //Limpar e terminar
    }
    while(1) {
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
            //TODO: decidir o que fazer
            printf("Erro no chamada select!\n");
        }

        //Caso algum FD esteja pronto para leitura
        else if (retSelect) {

            //Caso seja stdin, processa o comando
            if(FD_ISSET(0, &fdset)) {
                if(yyparse()) {
                    printf("Comando nao reconhecido! Digite \"help\" para obter ajuda.\n");
                }
            }

            //Caso seja a fifo, lê e atualiza instrumentos
            if(FD_ISSET(fifoFD, &fdset)) {
                bytes = read(fifoFD, readBuffer, 16);
                if(bytes != 16) {
                    //TODO: Lidar com isso?
                    printf("Dados incompletos! %d bytes lidos. Foi lido \"%s\"\n", bytes, readBuffer);
                } else {
                    printf("Dados show! %d bytes lidos. Foi lido \"%s\"\n", bytes, readBuffer);
                    camObjUpdate(&obj1, &obj2, readBuffer);
                    instrumentUpdate(&instr1, &obj1);
                    //instrumentUpdate(&instr2, &obj2);
                    instrumentWriteToCSound(instr1);
                    //instrumentWriteToCSound(instr2);
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

/*********************************
** THREADS DO PYTHON E DO CSOUND *
**********************************/

//TODO: Cleanup antes de retornar
void* imgProcessingThread(void *arg) {
    //Variaveis para chamar script python do processamento de imagem
    PyObject *pName, *pModule, *pDict, *pFunc, *pArgs, *pValue;

    Py_Initialize();
    //Importa codigo py da pasta /usr/lib/python2.7
    pName = PyUnicode_FromString((char*)"Imagem");
    pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    //Caso carregou com sucesso
    if (pModule != NULL) {
        //Obtem funcao mainLoop de Imagem.py
        pFunc = PyObject_GetAttrString(pModule, "mainLoop");

        //Caso encontrou a funcao
        if (pFunc && PyCallable_Check(pFunc)) {
            //Configura argumentos
            pArgs = PyTuple_New(3);

            //Arg 0 - Nome da FIFO
            pValue = PyString_FromString(fifoName);
                if (!pValue) {
                    Py_DECREF(pArgs);
                    Py_DECREF(pModule);
                    fprintf(stderr, "Cannot convert argument 0\n");
                    exit(1);
                }
            PyTuple_SetItem(pArgs, 0, pValue);

            //Arg 1 - Largura do frame
            pValue = PyLong_FromLong(FRAME_WIDTH);
                if (!pValue) {
                    Py_DECREF(pArgs);
                    Py_DECREF(pModule);
                    fprintf(stderr, "Cannot convert argument 1\n");
                    exit(1);
                }
            PyTuple_SetItem(pArgs, 1, pValue);

            //Arg 2 - Altura do frame
            pValue = PyLong_FromLong(FRAME_HEIGHT);
                if (!pValue) {
                    Py_DECREF(pArgs);
                    Py_DECREF(pModule);
                    fprintf(stderr, "Cannot convert argument 2\n");
                    exit(1);
                }
            PyTuple_SetItem(pArgs, 2, pValue);

            //Chama a funcao
            pValue = PyObject_CallObject(pFunc, pArgs);
            Py_DECREF(pArgs);
            if (pValue != NULL) {
                printf("Codigo python retornou! Algo errado?\n");
                Py_DECREF(pValue);
            }
            else {
                Py_DECREF(pFunc);
                Py_DECREF(pModule);
                PyErr_Print();
                fprintf(stderr,"Chamada python falhou\n");
                exit(1);
            }
        }
        else {
            if (PyErr_Occurred())
                PyErr_Print();
            fprintf(stderr, "Nao encontrou funcao mainLoop");
        }
        Py_XDECREF(pFunc);
        Py_DECREF(pModule);
    }
    else {
        PyErr_Print();
        fprintf(stderr, "Falha ao carregar modulo");
        exit(1);
    }
    Py_Finalize();    
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

/* Inicializa CameraObject */
void camObjInitialize(CameraObject* obj) {
    static int number = 1;
    obj->number = number;
    obj->state = 1;
    obj->x = 0;
    obj->y = 0;
}

/* Obtem da array de bytes crus (se tudo estiver certo, 24 bytes)
 * os valores atualizados para as posicoes e estados dos objetos */
void camObjUpdate(CameraObject* obj1, CameraObject* obj2, char* bytes) {
    if(bytes[0] == '-') {
        obj1->x = -1;
        obj1->y = -1;
        obj1->state = 0;
    } else {
        obj1->x = 100*(bytes[0]-'0') + 10*(bytes[1]-'0') + (bytes[2] - '0');
        obj1->y = 100*(bytes[4]-'0') + 10*(bytes[5]-'0') + (bytes[6] - '0');
        obj1->state = 1;
    }
    if(bytes[8] == '-') {
        obj2->x = -1;
        obj2->y = -1;
        obj2->state = 0;
    } else {
        obj2->x = 100*(bytes[9]-'0') + 10*(bytes[10]-'0') + (bytes[11] - '0');
        obj2->y = 100*(bytes[13]-'0') + 10*(bytes[14]-'0') + (bytes[15] - '0');
        obj2->state = 1;
    }
    printf("Objeto 1: %f %f, Objeto 2: %f %f\n", obj1->x, obj1->y, obj2->x, obj2->y);
}

/* Imprime parametros do CameraObject */
void camObjPrint(CameraObject obj) {
    printf("CAMERAOBJECT %d:\n", obj.number);
    printf("Estado: %d\n", obj.state);
    printf("(x,y): (%.1f, %.1f)\n\n", obj.x, obj.y);
}

/****************************************
* FUNCOES RELACIONADAS AOS INSTRUMENTOS *
*****************************************/

/* Inicializa um novo instrumento na configuracao padrao */
void instrumentInitialize(Instrument* instr) {
    static int instrNumber = 1;
    instr->number = instrNumber;
    instr->activated = 0;
    instr->state = 0;
    instr->type = 0;
    instr->frequency = 0;
    instr->amplitude = 0;
    instr->frequencyRange[0] = 300;
    instr->frequencyRange[1] = 600;
    instr->amplitudeRange[0] = 0;
    instr->amplitudeRange[1] = 30000;
    instr->masterVolume = 1;
    instr->numOfChannels = sizeof(instrumentChannels)/sizeof(*instrumentChannels);
    instrNumber++;
}

/* Atualiza um instrumento baseado num CameraObject */
void instrumentUpdate(Instrument* instr, CameraObject* obj) {
    float a,b;
    if(instr->activated == 0) {
        instr->state = 0;
        return;
    } else {
        instr->state = obj->state;
    }
    a = instr->frequencyRange[0];
    b = log(instr->frequencyRange[1]/instr->frequencyRange[0])/FRAME_WIDTH;
    instr->frequency = a*exp(b*obj->x);
    instr->amplitude = (instr->amplitudeRange[1]-instr->amplitudeRange[0])*(obj->y/FRAME_HEIGHT)*(instr->masterVolume)*MASTER_VOLUME;
    //printf("Frequencia: %f, amplitude: %f", instr->frequency, instr->amplitude);
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

/* Imprime todos os parametros do instrumento */
void instrumentPrint(Instrument instr) {
    printf("INSTRUMENTO %d:\n", instr.number);
    printf("Ativado: %d\n", instr.activated);
    printf("Estado: %d\n", instr.state);
    printf("Tipo: %d\n", instr.type);
    printf("Frequencia: %.1f\n", instr.frequency);
    printf("Amplitude: %.1f\n", instr.amplitude);
    printf("Intervalo de frequencias: %.1f-%.1f\n", instr.frequencyRange[0], instr.frequencyRange[1]);
    printf("Intervalo de amplitude: %.1f-%.1f\n", instr.amplitudeRange[0], instr.amplitudeRange[1]);
    printf("Volume mestre: %.1f\n\n", instr.masterVolume);
}


/*************************
* TRATAMENTO DE COMANDOS *
**************************/
void handleSetInstrPF(char* instr, char* param, float val) {
    Instrument* instrument;

    if(!strcmp(instr, "instr1")) {
        instrument = &instr1;
    }
    else if(!strcmp(instr, "instr2")) {
        instrument = &instr2;
    }
    else {
        printf("Comando nao reconhecido! Sintaxe: set instr[1-2] [state|type|mvolume] [0-1]\n");
    }

    if(!strcmp(param, "mvolume") && val >= 0 && val <= 1) {
        instrument->masterVolume = val;
    }
    else if(!strcmp(param, "activated")) {
        instrument->activated = (int)val;
    }
    else if(!strcmp(param, "type")) {
        instrument->type = (int)val;
    }
    else {
        printf("Comando nao reconhecido! Sintaxe: set instr[1-2] [state|type|mvolume] [0-1]\n");
    }
}

void handleSetInstrPFF(char* instr, char* param, float val1, float val2) {
    Instrument* instrument;

    if(!strcmp(instr, "instr1")) {
        instrument = &instr1;
    }
    else if(!strcmp(instr, "instr2")) {
        instrument = &instr2;
    }
    else {
        printf("Comando nao reconhecido! Sintaxe: set instr[1-2] [freqrange|amplrange] [float] [float]\n");
    }

    if(!strcmp(param, "freqrange")) {
        instrument->frequencyRange[0] = val1;
        instrument->frequencyRange[1] = val2;
    }
    else if(!strcmp(param, "amplrange")) {
        instrument->amplitudeRange[0] = val1;
        instrument->amplitudeRange[1] = val2;
    }
    else {
        printf("Comando nao reconhecido! Sintaxe: set instr[1-2] [freqrange|amplrange] [float] [float]\n");
    }
}


void handleSetPF(char* param, float val) {
    if(!strcmp(param, "mvolume") && val >= 0 && val <= 1) {
        MASTER_VOLUME = val;
    }
    else {
        printf("Comando nao reconhecido! Sintaxe: set mvolume [0-1]\n");
    }
}

void handlePrintP(char* param) {
    if(!strcmp(param, "mvolume")) {
        printf("Master volume: %f", MASTER_VOLUME);
    }
    else if(!strcmp(param, "fsize")) {
        printf("Largura do frame: %f, Altura do frame: %f\n", FRAME_WIDTH, FRAME_HEIGHT);
    }
    else if(!strcmp(param, "all")) {
        printf("Largura do frame: %f, Altura do frame: %f\n", FRAME_WIDTH, FRAME_HEIGHT);
        printf("Master volume: %f\n\n", MASTER_VOLUME);
        camObjPrint(obj1);
        camObjPrint(obj2);
        instrumentPrint(instr1);
        instrumentPrint(instr2);
    }
    else {
        printf("Comando nao reconhecido!\nSintaxe: print [mvolume|fsize|all]\n");
    }
}

void handlePrintInstr(char* instr) {
    if(!strcmp(instr, "instr1")) {
        instrumentPrint(instr1);
    }
    else if(!strcmp(instr, "instr2")) {
        instrumentPrint(instr2);
    }
    else {
        printf("Comando nao reconhedo!\nSintaxe: print instr[1-2]\n");
    }
}

//TODO: imprimir parametro
void handlePrintInstrP(char* instr, char* param) {
    Instrument instrument;

    if(!strcmp(instr, "instr1")) {
        instrument = instr1;
    }
    else if(!strcmp(instr, "instr2")) {
        instrument = instr2;
    }

    printf("TODO\n");


}

void handlePrintCamobj(char* camobj) {
    if(!strcmp(camobj, "camobj1")) {
        camObjPrint(obj1);
    }
    else if(!strcmp(camobj, "camobj2")) {
        camObjPrint(obj2);
    }
    else {
        printf("Comando nao reconhecido!\nSintaxe: print camobj[1-2]\n");
    }
}

//TODO: imprimir parametro
void handlePrintCamobjP(char* camobj, char* param) {
    printf("TODO\n");

}

//TODO: string de help
void handleHelp() {
    printf("Logo teremos um help kkkk\n");
}

//TODO: saida limpa
void handleExit() {
    printf("Para sair digite ctrl+c! Uma saida limpa ainda está sendo preparada.\n");
}









