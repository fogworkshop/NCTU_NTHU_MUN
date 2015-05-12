
if __name__ == '__main__':
    counter = 1
    print('id2nationality={', end='')
    nationality2id = {}
    while True:
        try:
            country = input();
        except:
            break
        nationality2id[country] = counter
        print('%d:"%s",'%(counter,country), end='')
        counter += 1
    print('}')
    print(nationality2id)
