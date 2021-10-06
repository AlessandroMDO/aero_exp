import numpy as np
from scipy import stats
from balance_signal import balance_signal
from data_acquisition import data_acquisition

def balanca_aerodinamica(dados_modelo, a_offset, ai, af, delta_a, freq_aq, n_ams, confianca):
    
    #Datsheet das constantes de calibração do soprador
    calib_lift = 131.1 # [N/V]
    calib_drag = 90.5 # [N/V]
    calib_mom = 8.56 # [N.m/V]
    
    gdl = n_ams - 1 # Graus de liberdade
    t = stats.t.ppf((confianca+100)/200, gdl) # Parâmetro t de Student
    
    t_aquisicao = (n_ams / freq_aq) # Tempo de aquisição, dado em [s]
    t_aquisicao_total = t_aquisicao * len(np.arange(ai, af+delta_a, delta_a)) # Tempo de aquisição total da simulação [s]
    
    
    offset_fore, offset_drag, offset_aft = balance_signal(-15, 'dados_asadelta.mat')[:-1]
    
    offset_fore = data_acquisition(offset_fore, freq_aq, n_ams)[0]
    offset_drag = data_acquisition(offset_drag, freq_aq, n_ams)[0]
    offset_aft = data_acquisition(offset_aft, freq_aq, n_ams)[0]
    
    
    offset_fore = np.mean(offset_fore) # Offset de fore [V]
    offset_drag = np.mean(offset_drag) # Offset de drag [V]
    offset_aft = np.mean(offset_aft) # Offset de aft [V]
    
    std_offset_fore = np.std(offset_fore) # Desvio padrão do offset de fore [V]
    std_offset_drag = np.std(offset_drag) # Desvio padrão do offset de drag [V]
    std_offset_aft = np.std(offset_aft) # Desvio padrão do offset de aft [V]
    
    error_offset_fore = t * std_offset_fore / np.sqrt(n_ams); # Cálculo do erro padrão (ver item 1.8 da apostila)
    error_offset_drag = t * std_offset_drag / np.sqrt(n_ams); # Cálculo do erro padrão (ver item 1.8 da apostila)
    error_offset_aft = t * std_offset_aft / np.sqrt(n_ams);
    

    alphas = np.arange(ai, af+delta_a, delta_a) 
    i = 0 
    Fore = np.zeros(len(alphas)) 
    Drag = np.zeros(len(alphas)) 
    Aft = np.zeros(len(alphas)) 
    Fore_error = np.zeros(len(alphas)) 
    Drag_error = np.zeros(len(alphas)) 
    Aft_error = np.zeros(len(alphas)) 
    P_din = np.zeros(len(alphas)) 
    P_din_error = np.zeros(len(alphas))
    
    
    for alpha in alphas:
        fore, drag, aft, p_din = balance_signal(alpha, dados_modelo) # Gera o sinal contínuo disponível nas células de carga para leitura

        fore = data_acquisition(fore, freq_aq, n_ams)[0] # Faz a aquisição do sinal disponível na célula de carga de fore
        drag = data_acquisition(drag, freq_aq, n_ams)[0] # Faz a aquisição do sinal disponível na célula de carga de drag
        aft = data_acquisition(aft, freq_aq, n_ams)[0] # Faz a aquisição do sinal disponível na célula de carga de aft
        p_din = data_acquisition(p_din, freq_aq, n_ams)[0] # faz a aquisição do sinal disponível no micromanômetro
    
        # Desvio Padrão
        fore_std = np.std(fore) # [V]
        drag_std = np.std(drag) # [V]
        aft_std = np.std(aft) # [V]
        p_din_std = np.std(p_din) # [Pa]
    
        # a leitura de interesse é a média dos pontos amostrados a partir do
        # sinal original menos o valor de offset (tara da balança)
        fore = np.mean(fore) - offset_fore # [V]
        drag = np.mean(drag) - offset_drag # [V]
        aft = np.mean(aft) - offset_aft # [V]
        pdin = np.mean(p_din) # [Pa]
        
        Fore[i] = fore # [V]
        Drag[i] = drag # [V]
        Aft[i] = aft # [V]
        P_din[i] = pdin # [Pa]
    
        # Calcula o erro das leituras em Volts (ou em Pa para o caso do micromanômetro)
        Fore_error[i] = t * fore_std / np.sqrt(n_ams) # [V]
        Drag_error[i] = t * drag_std / np.sqrt(n_ams) # [V]
        Aft_error[i] = t * aft_std / np.sqrt(n_ams) # [V]
        P_din_error[i] = max(0.01*pdin+1,t * p_din_std / np.sqrt(n_ams)) # [Pa] - no caso do micromanômetro, o erro fornecido pelo manual do fabricante é 1# da leitura +- 1 Pa, devemos usar o maior valor dentre os dois
        
        # Propagação do erro da operação de tara da balança
        Fore_error[i] = np.sqrt(Fore_error[i]**2 + error_offset_fore**2) # [V]
        Drag_error[i] = np.sqrt(Drag_error[i]**2 + error_offset_drag**2) # [V]
        Aft_error[i] = np.sqrt(Aft_error[i]**2 + error_offset_aft**2) # [V]
        
        # incrementa o contador do loop
        i = i + 1;
        
    #Página 51 da apostila    
    Lift = (Fore + Aft) * calib_lift # [N]
    Drag = Drag * calib_drag # [N]
    Moment = (Fore - Aft) * calib_mom # [N.m]
    
    #
    Lift_error = ((Fore_error**2 + Aft_error**2)**0.5) * calib_lift # [N]
    Drag_error = Drag_error * calib_drag; # [N]
    Moment_error = ((Fore_error**2 + Aft_error**2)**0.5) * calib_mom; # [N.m]
    

    return alphas, Lift, Drag, Moment, Lift_error, Drag_error, Moment_error, P_din, P_din_error, t_aquisicao_total
