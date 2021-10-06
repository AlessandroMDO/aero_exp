"""
Balança virtual

balance_signal(alpha, data_mat) é uma função
que simula um sinal analógico que seria lido nas células de carga de
uma balança e de um micromanômetro que produziram os resultados medidos 
experimentalmente encontrados no arquivo de matriz data_mat. A linha que 
possui pressão dinâmica nula corresponde à leitura da balança com o túnel 
desligado, para realização de tara (offset) da balança. A função realiza 
uma interpolação dos dados históricos para obter a leitura das células de 
carga em qualquer ângulo dentro do intervalo dos dados originais, 
acrescido de um ruído branco gaussiano que simula o ruído observado nos 
experimentos. fore, drag, aft e p_din são matrizes cuja primeira linha 
contém os instantes de tempo e a segunda linha contém os correspondentes 
valores de leitura em volts das células de carga e am Pa do micromanômetro.

Os valores da primeira linha da matriz data_mat são lidos diretamente 
da tabela de dados obtidos experimentalmente e são usados para o offset
(tara)
"""

import pandas as pd
import numpy as np
import scipy.io

def balance_signal(alpha, data_mat):
    
    dados_asadelta = scipy.io.loadmat(data_mat)
    table = pd.DataFrame(dados_asadelta['dados_asadelta'])
    
    if alpha == table.loc[0,0]:
        fore = table.loc[0,1]
        drag = table.loc[0,2]
        aft = table.loc[0,3]
        p_din = table.loc[0,7]
        
    else:
        
        fore = np.interp(alpha, table.loc[1:,0], table.loc[1:,1])
        drag = np.interp(alpha, table.loc[1:,0], table.loc[1:,2])
        aft = np.interp(alpha, table.loc[1:,0], table.loc[1:,3])
        p_din = np.interp(alpha, table.loc[1:,0], table.loc[1:,7])
        

    full_time = np.linspace(0, 10, 1000000, endpoint = True) # Tempo total do sinal pseudoanalógico em segundos e número de pontos
    
    fore_noise = np.sqrt(0.00005) * np.random.randn(1, len(full_time)) # O parâmetro dentro da raiz quadrada controla a intensidade do ruído
    drag_noise = np.sqrt(0.001) * np.random.randn(1, len(full_time)) # O parâmetro dentro da raiz quadrada controla a intensidade do ruído
    aft_noise = np.sqrt(0.00005) * np.random.randn(1, len(full_time)) # O parâmetro dentro da raiz quadrada controla a intensidade do ruído
    p_din_noise = np.sqrt(0.0001)* np.random.randn(1, len(full_time))
    
    
    fore = fore + fore_noise
    drag = drag + drag_noise
    aft = aft + aft_noise
    p_din = p_din + p_din_noise
    
    fore = np.vstack((full_time, fore))
    drag = np.vstack((full_time, drag))
    aft = np.vstack((full_time, aft))
    p_din = np.vstack((full_time,p_din))
    
    return fore, drag, aft, p_din
