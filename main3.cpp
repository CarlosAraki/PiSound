#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>

//g++ main.cpp -o output `pkg-config --cflags --libs opencv`

using namespace cv;


int main(int argc, char** argv)
{
    VideoCapture camera;
    if(!camera.open(0))
        return 0;
    for(;;)
    {
          Mat framein,frameout,frameout2,filter;
          camera >> framein;
           if( framein.empty() ) break;

          flip(framein,frameout,1); //espelho minha imagem
          cvtColor(frameout,frameout2,CV_BGR2GRAY);//converto em Cinza
          Mat pretobranco = frameout2 < 230; //apagando tudo q é cor sahshahas
          //Mat pretobranco = frameout2 < 120;
          GaussianBlur( pretobranco, filter, Size(5,5),0,0);
          imshow("camera zordera", filter);
          if( waitKey(10) == 27 ) break; // sai apertando ESC
    }

    return 0;
}
