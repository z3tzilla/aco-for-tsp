import sys
import numpy as np

class CityMap:
    """Карта расстояний с феромонами.
    
    Свойства:
    distances       - Матрица расстояний
    numberOfCities  - Количество городов
    pheromones      - Значения феромонов
    """
    def __init__(self, distancesMatrix: list, numberOfCities: int):
        """
        :param distancesMatrix: Матрица с расстояниями между городами
        :param numberOfCities: Количество городов
        """
        self.distances = distancesMatrix
        self.numberOfCities = numberOfCities
        self.pheromones = [[np.random.rand() for j in range(numberOfCities)] for i in range(numberOfCities)]

    def UpdatePheromones(self, evaporationRate: float, pheromoneDelta: list):
        """ Обновляет значения феромонов
        :param evaporationRate: коэффициент испарения феромона
        :param pheromoneDelta: матрица с изменениями феромонов от муравьёв
        """
        for i, row in enumerate(self.pheromones):
            for j, col in enumerate(row):
                self.pheromones[i][j] *= (1 - evaporationRate)
                self.pheromones[i][j] += pheromoneDelta[i][j]

class Ant:
    """Муравей
    
    Параметры:
    startingCity            - Начальный город
    currentCity             - Город, в котором находится муравей
    distance                - Дистанция, пройденная муравьём
    visitedCities           - Список посещённых городов
    """
    def __init__(self, startingCity:int):
        """
        :param startingCity: Начальный город муравья
        """
        self.startingCity = startingCity
        self.currentCity = startingCity
        self.distance = 0
        self.visitedCities = [startingCity]

    def Move(self, newCity:int, distance:int):
        """ Перемещает муравья в новый город
        :param newCity: Номер нового города
        :param distance: Дистанция между городами
        """
        self.currentCity = newCity
        self.visitedCities.append(newCity)
        self.distance += distance

class Colony:
    """Колония муравьёв

    Параметры:
    maxColonyCycles                 - Количество жизненных циклов колонии (сколько раз будут выпускаться муравьи)
    numberOfAnts                    - Количество муравьёв
    pheromoneAddition               - Количество феромона, откладываемое одним муравьём
    pheromoneEvaporationRate        - Коэффициент испарения феромона
    pheromoneImportance             - Коэффициент важности уровня феромона при поиске пути
    distanceImportance              - Коэффициент важности расстояния при поиске пути
    """
    maxColonyCycles = 50
    numberOfAnts = 500
    pheromoneAddition = 0.0005
    pheromoneEvaporationRate = 0.2
    pheromoneImportance = 0.01
    distanceImportance = 9.5
    antCanVisitPreviousCities = False

    def FindRoute(self, cityMap: CityMap):
        """ Поиск кратчайшего пути. Возвращает минимально найденную дистанцию.
        :param cityMap: Информация о городе
        """
        minDistance = float('inf')
        route = []

        for cycle in range(self.maxColonyCycles):
            pheromonesDelta = [[0.0 for i in range(cityMap.numberOfCities)] for j in range(cityMap.numberOfCities)]
            for antNumber in range(self.numberOfAnts):
                ant = Ant(np.random.randint(0, cityMap.numberOfCities))
                while len(ant.visitedCities) < cityMap.numberOfCities:
                    nextCity = self.GetNextCity(ant, cityMap)
                    ant.Move(nextCity, cityMap.distances[ant.currentCity][nextCity])
                antDistance = ant.distance + cityMap.distances[ant.currentCity][ant.startingCity]
                if antDistance < minDistance:
                    minDistance = antDistance
                    route = ant.visitedCities
                for city in range(len(ant.visitedCities) - 1):
                    pheromonesDelta[ant.visitedCities[city]][ant.visitedCities[city + 1]] += self.pheromoneAddition / antDistance
            cityMap.UpdatePheromones(self.pheromoneEvaporationRate, pheromonesDelta)

        return minDistance

    def GetProbabilities(self, ant: Ant, cityMap: CityMap):
        """Сформировать список вероятностей перемещения в города для указанного муравья.
        :param ant: Муравей, для которого производится поиск
        :param cityMap: Информация о городе
        """
        result = [0 for i in range(cityMap.numberOfCities)]
        totalProbability = 0
        for newCity in range(cityMap.numberOfCities):
            if (newCity != ant.currentCity) and (self.antCanVisitPreviousCities or newCity not in ant.visitedCities):
                probability = pow(cityMap.pheromones[ant.currentCity][newCity], self.pheromoneImportance) * pow(1 / cityMap.distances[ant.currentCity][newCity], self.distanceImportance)
                result[newCity] = probability
                totalProbability += probability
        result = [result[i] / totalProbability for i in range(cityMap.numberOfCities)]
        return result

    def GetNextCity(self, ant:Ant, cityMap:CityMap):
        """ Выбрать следующий город для муравья. Возвращает номер города или -1 если нет подходящего.
        :param ant: Муравей, для которого производится поиск
        :param cityMap: Информация о городе
        """
        probabilities = self.GetProbabilities(ant, cityMap)
        randomValue = np.random.rand()
        for i in range(cityMap.numberOfCities):
            if probabilities[i] > randomValue:
                return i
            else:
                randomValue -= probabilities[i]
        return -1

matrix = np.loadtxt(sys.stdin, dtype=np.int)
cityMap = CityMap(matrix, len(matrix[0]))
colony = Colony()
result = colony.FindRoute(cityMap)
print(result)