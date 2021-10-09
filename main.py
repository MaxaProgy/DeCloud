from plot import Plot
from blockchain import blockchain



if __name__ == '__main__':
    plot = Plot()
    plot.load_from_file("Инфографика ШЛ ОК 2021.pdf")
    plot.save_data("Инфографика ШЛ ОК 2021.pdf")
    print(blockchain.transaction)
