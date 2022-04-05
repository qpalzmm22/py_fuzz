from pythonfuzz.main import PythonFuzz


@PythonFuzz
def fuzz(buf):
    try:
        string = buf.decode("ascii")
        if len(string) == 3:
            # print('success')
            if string[0] == 'f':
                if string[1] == 'u':
                    if string[2] == 'z':
                        raise Exception('nice')
                    elif string[2] == 'b':
                        raise Exception('good')
            #     raise Exception('nice')
            # if string[0] == 'f' and string[1] == 'u' and string[2] == 'z':
            #     raise Exception('nice')

    except UnicodeDecodeError:
        pass


if __name__ == '__main__':
    fuzz()
