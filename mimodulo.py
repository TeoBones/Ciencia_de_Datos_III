# -*- coding: utf-8 -*-
"""MiModulo.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1N9MFv-zHAJZeP22XNeMT4MJYIAIp-_x4
"""

from google.colab import drive
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
from scipy.stats import norm
from scipy.stats import shapiro
from sklearn.metrics import auc

"""
MiModulo
-------------------------

Este módulo proporciona una clase para realizar cálculos de regresión lineal simple, múltiple, y regresión logística utilizando librerías:
- pandas
- numpy
- statsmodels
- scipy
- matplotlib
- sklearn

Clases:
    Regresion: Clase madre de RegresionLineal y RegresionLogistica. Realiza tests de supuestos y predicciones de nuestro modelo.

    RegresionLineal: Ajusta nuestro modelo de regresión lineal (tanto simple como multiple) y grafica la dispersion de datos con nuestra recta ajustada.

    RegresionLogistica: Ajusta nuestro modelo de regresión logistica e implementa una matriz de confusion y método relacionados sobre un entrenamiento de datos.
"""

class Regresion:
    def __init__(self, x, y):
        """
        Constructor de la clase Regresion, se desginan los atributos:

        x: variables predictoras
        y: variables respuestas
        X: matriz de diseño de variables predictoras
        __ajuste: corrobora si se realizó el método modelar.()
        
        """
        self.x = x
        self.y = y
        self.X = sm.add_constant(x)
        self.__ajuste = True

    def predecir(self, new_x):
        """
        Predice la respuesta de una muestra de variable predictoras, utiliza el método .modelar() para realizar la predicción

        Args:
            new_x (float or np.darray): Variable predictora

        Returns:
            predichos (pd.DataFrame or np.darray, dtype=float):  Respuesta predicha de nuestra variable predictora
        """
        if self.__ajuste == False:
            print("Error. Aplicar el método \".modelar()\" antes de utilizar .predecir()")
        else:
            new_X = sm.add_constant(new_x)
            predichos = (self.modelo).predict(new_X)
            return predichos

    def intervalos(self, new_x, alfa=0.05):
        """
        Predice la respuesta de una muestra de variables predictoras, utiliza el método .modelar() para realizar la predicción

        Args:
            new_x (float): Variable predictora

        Returns:
            int_confianza[0] (pd.DataFrame or np.darray, dtype=float): Intervalo de confianza para la respuesta predicha de new_x
            int_prediccion[0] (pd.DataFrame or np.darray, dtype=float): Intervalo de predicción para la respuesta predicha de new_x
        """
        if self.__ajuste == False:
            print("Error. Aplicar el método \".modelar()\" antes de utilizar .predecir()")
        else:
            new_X = sm.add_constant(new_x)
            prediccion = self.modelo.get_prediction(new_X)

            int_confianza = prediccion.conf_int(alpha = alfa)
            int_prediccion = prediccion.conf_int(obs = True, alpha = alfa)

            return int_confianza[0], int_prediccion[0]

    def homocedasticidad(self):
        """
        Evalua la constancia de la varianza del error de nuestro modelo mediante un test de hipotesis,

        h0: Los errores tienen varianza constante
        h1: Los errores NO tienen varianza constante

        devuelve un print con el p-valor de dicho test
        """
        if self.__ajuste == False:
            print("Error. Aplicar el método \".modelar()\" antes de utilizar .homocedasticidad()")
        else:
            bp_test = het_breuschpagan(self.resid, self.X)
            bp_value = bp_test[1]
            print("Valor p Homocedasticidad:", bp_value)

    def normalidad(self):
        """
        Evalua la normalidad del error de nuestro modelo mediante un test de hipotesis,

        h0: La distribución de los errores es normal
        h1: La distribución de los errores NO es normal

        devuelve un print con el p-valor de dicho test
        """
        data = self.resid
        media = np.mean(data)
        desviacion_estandar = np.std(data)

        data_s = (data- media) / desviacion_estandar
        cuantiles_muestrales=np.sort(data_s)
        n=len(data)
        pp=np.arange(1, (n+1))/(n+1)
        cuantiles_teoricos = norm.ppf(pp)

        plt.scatter(cuantiles_teoricos, cuantiles_muestrales, color='blue', marker='o')
        plt.xlabel('Cuantiles teóricos')
        plt.ylabel('Cuantiles muestrales')
        plt.plot(cuantiles_teoricos,cuantiles_teoricos , linestyle='-', color='red')
        plt.show()

        stat, p_valor1 = shapiro("datos")
        print("Valor p normalidad:", p_valor1)
#--------------------------------------------------------------------------------------------------------------------#

class RegresionLineal(Regresion):
    def __init__(self, x, y):
        """
        Llama al constructor de la clase Regresion
        """
        super().__init__(x, y)

    def modelar(self):
        """
        Realiza el ajuste de nuestro modelo de Regresion Lineal. Guarda los siguientes atributos en nuestra instancia de clase:

            self.modelo: Objeto de nuestro modelo ajustado de la libreria statsmodels.
            self.params: Coeficientes de nuestro modelo.
            self.rsquared_adj: Medida corregida de la precisión de nuestro modelo, 1 si es excelente, 0 si es pésimo.
            self.resid: Residuos de nuestro modelo
            self.se: Errores estándar de los coeficientes estimados de nuestro modelo
            self.t_obs: el t_estadístico de los coeficientes estimados de nuestro modelo

        También devuelve en un print una tabla con un resumen numérico del modelo
        """
        self.__ajuste = True
        model = sm.OLS(self.y, self.X)
        result = model.fit()
        print(result.summary())

        self.modelo = result
        self.params = result.params
        self.rsquared_adj = result.rsquared_adj
        self.resid = result.resid
        self.se = result.bse
        self.t_obs = result.tvalues

    def graficar_recta_ajustada(self):
        """
        Grafica la recta ajustada por cada variable predictora
        """
        if self.__ajuste == False:
          print("Error. Aplicar el método \".modelar()\" antes de utilizar .graficar_recta_ajustada()")
        else:
            try:
                (self.x).shape[1]
            except IndexError: #Caso de Regresion Lineal Simple
                plt.scatter(self.x, self.y)
                pred_y = (self.modelo).predict(self.x)
                plt.plot(self.x, pred_y)

            else: #Caso de Regresion Lineal Multiple
                for i in range(self.x.shape[1]):
                    x_aux = self.x[:,i]
                    X_aux = sm.add_constant(x) #Creo un modelo de Regresion Lineal Simple por cada predictora
                    modelo_aux = sm.OLS(self.y, X_aux)
                    ajuste_aux = modelo_aux.fit()

                    plt.scatter(x_aux, self.y)
                    pred_y = ajuste_aux.predict(X_aux)
                    plt.plot(self.x[:,i], pred_y);

#--------------------------------------------------------------------------------------------------------------------#

class RegresionLogistica(Regresion):
    def __init__(self, x, y):
        """
        Llama al constructor de la clase Regresion
        """
        super().__init__(x, y)

    def modelar(self):
        """
        Realiza el ajuste de nuestro modelo de Regresion Logistica. Guarda los siguientes atributos en nuestra instancia de clase:

            self.modelo: Objeto de nuestro modelo ajustado de la libreria statsmodels.
            self.params: Coeficientes de nuestro modelo.
            self.rsquared_adj: Medida corregida de la precisión de nuestro modelo, 1 si es excelente, 0 si es pésimo.
            self.resid: Residuos de nuestro modelo
            self.se: Errores estándar de los coeficientes estimados de nuestro modelo
            self.t_obs: el t_estadístico de los coeficientes estimados de nuestro modelo

        También devuelve en un print una tabla con un resumen numérico del modelo
        """
        model = sm.Logit(self.y, self.X)
        result = model.fit()
        print(result.summary())

        self.modelo = result
        self.params = result.params
        self.se = result.bse
        self.t_obs = result.tvalues
        self.__ajuste = True

    def entrenar(self, k=0.8):
        """
        Entrena el modelo de regresión logística usando la librería statsmodels.

        Args:
            k (float): Porcentaje de datos utilizados para entrenar al modelo, por default k=0.8.

        Returns:
            test_y (pd.DataFrame or np.darray, dtype=int): Respuestas en la muestra de testeo
            pred_y_prob (pd.DataFrame or np.darray, dtype=float): Probabilidad de las predichas en la muestra de testeo
        """
        if isinstance(self.y, pd.DataFrame):
            test_ind = random.sample(range(len(self.y)), int(len(self.y)*k))  # Generamos un array de los "indices" con los que armo el conjunto entrenador y test

            train_X = (self.X).iloc[test_ind]  # Conjuntos de entrenamiento
            train_y = (self.y).iloc[test_ind]
            test_X = (self.X).drop(test_ind)  # Conjuntos de test
            test_y = (self.y).drop(test_ind)

        elif isinstance(self.y, np.ndarray):
            indices = np.arange(len(self.y))
            test_ind = np.random.choice(indices, size=int(len(self.y) * (1 - k)), replace=False)

            train_X = np.delete(self.X, test_ind, axis=0)  # Conjuntos de entrenamiento
            train_y = np.delete(self.y, test_ind, axis=0)
            test_X = self.X[test_ind]  # Conjuntos de test
            test_y = self.y[test_ind]

        else:
            print("Error. el conjunto de datos debe ser numpy.ndarray o pandas.DataFrame")
            return None, None

        modelo_train = sm.Logit(train_y, train_X)  # Ajustamos nuestro modelo entrenador
        modelo_train = modelo_train.fit()
        pred_y_prob = modelo_train.predict(test_X)  # Predicción de las respuestas "test" sobre el modelo ajustando sobre "train"

        return test_y, pred_y_prob

    def matriz_confusion(self, p=-1, k=0.8):
        """
        Realiza una matriz de confusión con el modelo entrenado, utiliza el método .entrenar(p,k)

        Args:
            k (float): Porcentaje de datos utilizados para entrenar al modelo. Por default k=0.8
            p (float): punto de corte, si p=-1 encuentra el punto de corte óptimo segun el índice de Youden. Por default p=-1

        Returns:
            matriz_confusion (np.darray, dtype=int): Genera un array con dos vectores representando las dos filas en la matriz de confusión.
        """

        test_y, pred_y_prob = self.entrenar(k)

        if p == -1: #Encontraremos p a partir del Índice de Youden
            p_max = 0
            aux_max = 0 #en este auxiliar almacenaremos la cuenta: [sensibilidad(p_max) + especificidad(p_max) - 1]
            matriz_confusion_max = 0
            grilla = np.linspace(0,1,100) #grilla con los puntos de cortes a evalauar

            for p in grilla:
                pred_y = 1 * (np.array(pred_y_prob) >= p) #convertimos nuestra prediccion dada por probabilidad en un booleano siguiendo el punto de corte
                print(pred_y)
                matriz_confusion = np.array([[sum((pred_y == 1) & (test_y == 1)), sum((pred_y == 1) & (test_y == 0))], #generamos la matriz de confusion para cada p en grilla
                                             [sum((pred_y == 0) & (test_y == 1)), sum((pred_y == 0) & (test_y == 0))]])

                sensibilidad_p = matriz_confusion[0,0]/(matriz_confusion[0,0] + matriz_confusion[1,0]) #calculamos sensibilidad
                especificidad_p = matriz_confusion[1,1]/(matriz_confusion[1,1] + matriz_confusion[0,1]) #calculamos especificidad

                if (sensibilidad_p + especificidad_p - 1) > aux_max: #si se cumple la condición:
                    p_max = p #actualizamos p_max
                    aux_max = (sensibilidad_p + especificidad_p - 1) #actualizamos aux_max
                    matriz_confusion_max = matriz_confusion
            print("el punto de corte óptimo es", p_max)

        else:
            pred_y = 1 * (np.array(pred_y_prob) >= p) #convertimos nuestra prediccion dada por probabilidad en un booleano siguiendo el punto de corte
            matriz_confusion = np.array([[sum((pred_y == 1) & (test_y == 1)), sum((pred_y == 1) & (test_y == 0))], #generamos la matriz de confusion para p
                                         [sum((pred_y == 0) & (test_y == 1)), sum((pred_y == 0) & (test_y == 0))]])

        return matriz_confusion

    def ROC(self, k=0.8):
        """
        Realiza y grafica una curva ROC. Utiliza el método .matriz_confusion(p,k)

        Args:
            k (float): Porcentaje de datos utilizados para entrenar al modelo. Por default k=0.8

        Returns:
            AUC (float): Area Under the Curve, devuelve
        """
        grilla_p = np.linspace(0, 1, 100)

        sensibilidad = np.zeros(len(grilla_p))
        especificidad = np.zeros(len(grilla_p))

        for i in range(len(grilla_p)):
            sensibilidad[i] = self.matriz_confusion(grilla_p[i], k)[0,0]
            especificidad[i] = self.matriz_confusion(grilla_p[i], k)[1,1]

        plt.plot(1 - especificidad, sensibilidad)

        AUC = auc(1 - especificidad, sensibilidad)

        if AUC <= 0.6:
          print('Modelo fallido.')
        elif 0.6 < AUC <= 0.7:
          print('Modelo pobre')
        elif 0.7 < AUC <= 0.8:
          print('Modelo regular.')
        elif 0.8 < AUC <= 0.9:
          print('Modelo bueno.')
        else:
          print('Modelo excelente.')

        return AUC