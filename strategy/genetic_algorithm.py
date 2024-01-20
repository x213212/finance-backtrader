import strategy.popular_model as popmoder

import datetime 
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import urllib.request; #用來建立請求
from concurrent.futures import ThreadPoolExecutor
import strategy.bband as bb
import strategy.rsi as rsi
import strategy.arron as arron
import numpy as np
import random

# 生成一個基因片段，包含n個區間的交易策略
def generate_chromosome(n_intervals, historical_days ,strategies ):
    chromosome = []
    days = list(range(historical_days))
    random.shuffle(days)
    intervals = sorted(random.sample(days, n_intervals * 2))
    for i in range(0, n_intervals * 2, 2):
        start_day = intervals[i]
        end_day = intervals[i+1]
        strategy = random.choice(strategies)
        gene = (start_day, end_day, strategy)
        chromosome.append(gene)
    return chromosome

def check_strategie_single(day, get_strategoes_signel, chromosome, process_mode):
    day_int = day
    signal_index = 2 if process_mode else 3
    for start_int, end_int, strategy_key in chromosome:
        if start_int <= day_int <= end_int:
            strategy_signals = get_strategoes_signel[strategy_key]
            if day_int in strategy_signals[signal_index]:
                return True
    return False
    
def calculate_fitness(chromosome, data_param, get_strategoes_signel):
    star, price, ex_handle, buy_list, sell_list, data_list, data_list2, data_list3, start, end, str_tmp, ope, close, high, low, vol, date, date_ex, now_stock, model = data_param
    data_count = len(data_list)
    fin_price = 0
    handle = 0
    re_handle = 0

    for tmp in range(data_count):
        close_tmp = close[tmp]
        ex_handle = int(price / (close_tmp * 1000)) - 1
        
        if check_strategie_single(tmp, get_strategoes_signel, chromosome, True) and price >= (ex_handle * close_tmp * 1000):
            handle += ex_handle * 1000
            re_handle += ex_handle
            fin_price = price - (ex_handle * ope[tmp + 1]) * 1000
            price = fin_price
        elif check_strategie_single(tmp, get_strategoes_signel, chromosome, False) and re_handle >= 1:
            fin_price = price + (re_handle * close_tmp) * 1000
            handle = 0
            re_handle = 0
            price = fin_price

    if handle > 0:  # 強制平倉
        fin_price += (close[-1] * handle)
        handle = 0
        re_handle = 0

    return fin_price


def crossover(parent1, parent2, historical_days):
    cross_point = random.randint(1, len(parent1) - 2)
    child1 = parent1[:cross_point] + parent2[cross_point:]
    child2 = parent2[:cross_point] + parent1[cross_point:]

    child1 = trim_chromosome(child1, historical_days)
    child2 = trim_chromosome(child2, historical_days)

    return child1, child2

def trim_chromosome(chromosome, historical_days):
    # 确保基因片段的总天数不超过历史天数限制
    # 这里简化处理：如果总天数超过历史天数，就随机删除一些区间
    while sum([end - start for start, end, _ in chromosome]) > historical_days:
        chromosome.pop(random.randint(0, len(chromosome) - 1))
    return chromosome

def mutate(chromosome, mutation_rate, strategies, historical_days):
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            start_day, end_day, _ = chromosome[i]
            new_strategy = random.choice(strategies)
            chromosome[i] = (start_day, end_day, new_strategy)

    chromosome = trim_chromosome(chromosome, historical_days)
    return chromosome
def select_parents(population, fitness_scores):
    fitness_sum = sum(fitness_scores)
    if fitness_sum == 0:
        return random.sample(population, 2)  # 如果所有适应度都是0，则随机选择

    # 计算每个个体的选择概率
    selection_probs = [fitness / fitness_sum for fitness in fitness_scores]

    # 依概率选择两个父代
    parent1 = random.choices(population, weights=selection_probs, k=1)[0]
    parent2 = random.choices(population, weights=selection_probs, k=1)[0]

    return parent1, parent2
# 基因演算法主程序（簡化版）
def genetic_algorithm(n_intervals, population_size, mutation_rate, generations, strategies,data_param):
    get_strategoes_signel = {}
    for get_strategie in strategies:
        # print(get_strategie)
        if get_strategie == "BBand":
            get_strategoes_signel[get_strategie ] = bb.bband(data_param)
        elif get_strategie == "Rsi": 
            get_strategoes_signel[get_strategie ] = rsi.rsi(data_param)
        elif get_strategie == "Arron":
            get_strategoes_signel[get_strategie ] = arron.arron(data_param)
            
    population = [generate_chromosome(n_intervals, len(data_param[5]),  strategies) for _ in range(population_size)]
    for g in range(generations):
        # 计算适应度
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(calculate_fitness, chromosome, data_param, get_strategoes_signel) for chromosome in population] 
            fitness_scores = [future.result() for future in futures]
        # 选择
        sorted_population = sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)
        selected = [chromosome for _, chromosome in sorted_population[:population_size // 2]]

        # 保留当前代的前五个最优基因
        elites = [chromosome for _, chromosome in sorted_population[:5]]

        # 交叉和突变
        new_population = elites.copy()
        while len(new_population) < population_size:
            parent1, parent2 = select_parents(selected, fitness_scores[:len(selected)])
            child1, child2 = crossover(parent1, parent2, len(data_param[5]))
            new_population.append(mutate(child1, mutation_rate, strategies, len(data_param[5])))
            new_population.append(mutate(child2, mutation_rate, strategies, len(data_param[5])))

        # 更新种群
        population = new_population

        # 打印当前代的最佳适应度
        print(f"Generation {g}: Best Fitness = {sorted_population[0][0]} {sorted_population[0][1]}")

    # 選擇最佳個體
    best_chromosome = population[0]

    return best_chromosome
