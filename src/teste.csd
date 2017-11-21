<CsoundSynthesizer>
<CsOptions>
-o dac
</CsOptions>
<CsInstruments>
; Inicializa as variáveis globais.
sr = 44100
kr = 4410
ksmps = 10
nchnls = 1

;Instrumento #1.
instr 1
    ;Estado do instrumento
    kState init 0
    kState chnget "instr1State"

    ;Tipo do instrumento
    kType init 0
    kType chnget "instr1Type"

    ;Frequência
    kFreq init 0
    kFreq chnget "instr1Freq"

    ;Amplitude do sinal
    kAmp init 0
    kAmp chnget "instr1Ampl"

    ;Número da f-table.
    ifn = 1
    ;Toca com amplitude 30000 e frequência de gkFreq Hz a onda do seno
    ;armazenada na tabela 1.
  
    ;Manda o som armazenado em a1 para a saida de audio 
    a1 oscil kAmp, kFreq, ifn
    out a1
endin

/*;Instrumento #2.
instr 2
    ;Estado do instrumento
    kState init 0
    kState chnget "instr2State"

    ;Tipo do instrumento
    kType init 0
    kType chnget "instr2Type"

    ;Frequência
    kFreq init 0
    kFreq chnget "instr2Freq"

    ;Amplitude do sinal
    kAmp init 0
    kAmp chnget "instr2Ampl"

    ;Número da f-table.
    ifn = 1
    ;Toca com amplitude 30000 e frequência de gkFreq Hz a onda do seno
    ;armazenada na tabela 1.
  
    ;Manda o som armazenado em a1 para a saida de audio 
    a1 oscil kAmp, kFreq, ifn
    out a1
endin*/ 

</CsInstruments>
<CsScore>
; Tabela #1: uma simples onda de seno usando GEN10.
f 1 0 16384 10 1
; Toca o instrumento #1 por 2 segundos, começando em 0 segundos
i 1 0 120
;i 2 0 120
e
</CsScore>
</CsoundSynthesizer> 
