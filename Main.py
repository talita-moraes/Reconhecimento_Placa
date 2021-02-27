import cv2
import pytesseract as ocr
import numpy  as np
import matplotlib.pyplot as plt
import imutils
from PIL import Image
import tkinter
import time
font = cv2.FONT_HERSHEY_COMPLEX

cont = 0
cap = cv2.VideoCapture(0)
cap.set(3, 1280)           
cap.set(4, 720)

#metodos 
def V_cinza(img):
      cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)         #video em cinza
      return cinza

def V_canny(img):
      canny = cv2.Canny(img,100,200)                        #video em canny
      return canny

def V_RGB(img):
      npimagem = np.asarray(img).astype(np.uint8)          # convertendo em um array editável de numpy[x, y, CANALS]

      # diminuição dos ruidos antes da binarização
      npimagem[:, :, 0] = 0 # zerando o canal R (RED)
      #npimagem[:, :, 2] = 0 # zerando o canal G (GREEN)
      npimagem[:, :, 1] = 0 # zerando o canal B (BLUE)

      # aplicação da truncagem binária para a intensidade
      # pixels de intensidade de cor abaixo de 127 serão convertidos para 0 (PRETO)
      # pixels de intensidade de cor acima de 127 serão convertidos para 255 (BRANCO)
      # A atrubição do THRESH_OTSU incrementa uma análise inteligente dos nivels de truncagem
      ret, thresh = cv2.threshold(V_cinza(npimagem), 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  #Pode ser tanto 127 ou 90
      #ret, thresh = cv2.threshold(V_cinza(npimagem), 90, 255, cv2.THRESH_BINARY)
      return thresh

def Processamento(img,img2):
    contornos = cv2.findContours(V_canny(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contornos = imutils.grab_contours(contornos)
    contornos = sorted(contornos, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None
    imagem = img

    for c in contornos:
        perimetro = cv2.arcLength(c, True)                                  # perimetro do contorno, verifica se o contorno é fechado
        #print(perimetro)
        
        if perimetro >= 150 and perimetro <= 1000 :
            approx = cv2.approxPolyDP(c, 0.015 * perimetro, True)           #aproxima os contornos da forma correspondente

            if len(approx) == 4:                                            # verifica se é um quadrado ou retangulo de acordo com a qtd de vertices
                cv2.drawContours(imagem, [approx], -1, (0,255, 0), 2)      #Contorna a placa atraves dos contornos encontrados em verde se ajusta com o quadrado
                
                (x, y, lar, alt) = cv2.boundingRect(c)
                #cv2.rectangle(imagem, (x, y), (x + lar, y + alt), (255, 0, 0), 2)     Contorna a placa atraves dos contornos encontrados em azul sem ajusta 
                particao = img[(y):y+alt, x:x+lar]  #segmenta a placa da imagem

                frase = ReconhecimentoTexto(V_cinza(particao))
                #frase = ReconhecimentoTexto(V_RGB(particao))
                #frase = ReconhecimentoTexto(particao)
                #print(frase)                
                
                cv2.imwrite('Texto1.png',V_cinza(particao)) #Salva imagem em texto
                cv2.imwrite('Texto2.png',V_RGB(particao))
                
                if(frase != None):
                      cv2.putText(imagem, "Placa: ", (131, 90), font, 1,(0,255, 0), 2)
                      cv2.imshow("1", imagem)
                      cv2.imwrite(str(cont)+'-Foto.png',imagem)
                      #cv2.imshow("Porcao", particao)
                      
                      print(frase)
                      return frase 
            
def ReconhecimentoTexto(im):
      im = cv2.resize(im, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)    #ampliação de 3 vezes o seu tamanho original
      #cv2.imshow("Tes1", im)
      binimagem = Image.fromarray(im)                       # reconvertendo o retorno do threshold em um objeto do tipo PIL.Image
      frase = ocr.image_to_string(binimagem, lang='eng')    # chamada ao tesseract OCR por meio de seu wrapper

      #print (len (frase))
      if(len(frase) > 0 ) :
            #print (frase)            
            frase = RemoverCaracteres(frase)    #tratamento da imagem          
            #print (frase)
            return frase
      #else:
            #frase = "Reconhecimento Falho"
     
def RemoverCaracteres(frase):
    str = "!@#%¨&*()_+:;><^^}{'`?|~'[]$¬\/=,.'ºª»‘"
    for x in str:
        frase = frase.replace(x, '')
        
    return frase

def Graf(img,cont,texto):                                         #gerar grafico
    plt.imshow(V_cinza(img),cmap = plt.get_cmap('gray'))
    plt.xticks([]), plt.yticks([])
    plt.title('Placa: '+texto)
    print("Imagem Cinza Plotanda")
    plt.savefig(str(cont)+'-Plot.png')
    plt.show()

    janela = tkinter.Tk()
    tkinter.Label(janela, text=texto, font=("Helvetica", 50)).pack()
    janela.mainloop()

    cont = cont +1

    
#main - Loop principal
while True:

    #verificação da existencia da camera
    if cap.isOpened():                   
        rval, img = cap.read()
        rval, img2 = cap.read() 
    else:
        rval = False
        print ('erro: não há camera conctada \n\n')        
        os.system("pause")
        if img is None:
              break

    #Resolução da camera
    #cv2.namedWindow('original', cv2.WINDOW_NORMAL)
    #cv2.resizeWindow('original', 800,600)

    #Estudos dos filtro de cores
    cv2.imshow("original", img)
    #cv2.imshow("cinza", V_cinza(img))
    #cv2.imshow("canny", V_canny(img))
    #cv2.imshow("RGB", V_RGB(img))
    
    Processamento(img, img2)

    if(Processamento(img, img2) != None):
          texto = Processamento(img, img2)
    
    if cv2.waitKey(1) & 0xFF == ord('2'):  # Plotar imagem
          Graf(img,cont,texto) 
    elif  cv2.waitKey(100) & 0x0f == 0x0b: # espera pela tecla 'esc' para sair
          break

cap.release()
cv2.destroyAllWindows()

