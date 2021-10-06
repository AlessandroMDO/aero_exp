"""
Placa de aquisição virtual

data_acquisition(time_series, sampling_rate, number_of_samples) é uma função 
que simula uma placa de aquisição que recebe um sinal time_series e realiza uma 
amostragem desse sinal a uma taxa de amostragem de sampling_rate amostras por segundo,
coletando um número number_of_sample de amostras. A função fornece duas
saídas, a primeira sendo um vetor com os pontos amostrados do sinal e a
segunda sendo um vetor que contem os instantes de tempo nos quais o sinal
foi amostrado. Devido à maneira como a função balance_signal foi
implementada, não deve ser usado uma taxa de amostragem maior que 10000
amostras por segundo e o número de amostras deve ser tal que a duração da
aquisição não ultrapasse 5 minutos (300 segundos).
"""


import numpy as np

def data_acquisition(time_series, sampling_rate, number_of_samples):
    
    final_time = number_of_samples / sampling_rate # Obtém o instante de tempo em que a aquisiçao será encerrada
    acquisition_time = np.linspace(1e-3, final_time, number_of_samples, endpoint = True) # Define os instantes de tempo em que o sistema coletará uma amostra do sinal da balança, com um delay inicial de 1 ms

    sampled_data = np.interp(acquisition_time, time_series[0,:], time_series[1,:]) # Registra o sinal da balança nos instantes de tempo definidos para a amostragem
    
    
    return sampled_data, acquisition_time