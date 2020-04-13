import argparse

def initialize():
    parser = argparse.ArgumentParser(description='''
Reads a file, and outputs the repl commands to write the contents again to disk.
Useful to copy executable code to micropython systems using the paste mode once.
Write code, run this program on the file, paste the output on the micropython serial interface.''',
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('src', type=str, help='File containing contents to be transferred')
    parser.add_argument('--dest', help='Filename of destination file on the micropython system, default is src_file name')
    args = parser.parse_args()
    init_vars = {
        'src_file': args.src,
        'dest_file': args.dest
    }
    return init_vars
    
if __name__ == "__main__":
    init = initialize()
    if init['dest_file'] == None:
        init['dest_file'] = init['src_file']
        print(f"Destination filename: {init['dest_file']}")
    print('Copy and paste from below:\n\n')
    print(f"with open('{init['dest_file']}', 'w+') as f:")
    with open(init['src_file']) as f:
        file_contents = f.readlines()
    for line in file_contents:
        print('    f.write("' + line.strip('\n') + '\\n")')