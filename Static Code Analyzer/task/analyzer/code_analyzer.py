import os
import sys
import re
import ast
import astunparse

# write your code here
class CustomLenException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S001 Too long".format(i)
        # self.message = str(os.path.relpath(os.getcwd())) + ": Line {}: S001 Too long".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomIndenFourException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S002 Indentation is not a multiple of four".format(i)
        # self.message = str(os.path.relpath(os.getcwd())) + ": Line {}: S002 Indentation is not a multiple of four".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomUnnSemicolonException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S003 Unnecessary semicolon after a statement".format(i)
        # self.message = str(os.path.relpath(os.getcwd())) + ": Line {}: S003 Unnecessary semicolon after a statement".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomLessThanTwoSpacesException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S004 Less than two spaces before inline comments".format(i)
        # self.message = str(os.path.relpath(os.getcwd())) + ": Line {}: S004 Less than two spaces before inline comments".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomTODOFoundException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S005 TODO found".format(i)
        # self.message = str(os.path.relpath(os.getcwd())) + ": Line {}: S005 TODO found".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomMoreThanTwoBlanksException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S006 More than two blank lines preceding a code line".format(i)
        # self.message = str(os.path.relpath(os.getcwd())) + ": Line {}: S006 More than two blank lines preceding a code line".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomTooManySpacesException(Exception):
    def __init__(self, i, structure_name, path_):
        self.message = str(path_) + ": Line {}: S007 Too many spaces after '{}'".format(i, structure_name)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomCamelCaseException(Exception):
    def __init__(self, i, class_name, path_):
        self.message = str(path_) + ": Line {}: S008 Class name '{}' should use CamelCase".format(i, class_name)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomSnakeCaseException(Exception):
    def __init__(self, i, func_name, path_):
        self.message = str(path_) + ": Line {}: S009 Function name '{}' should use snake_case".format(i, func_name)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomArgNameSnakeCaseException(Exception):
    def __init__(self, i, arg_name, path_):
        self.message = str(path_) + ": Line {}: S010 Argument name '{}' should be written in snake_case".format(i, arg_name)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomVarNameSnakeCaseException(Exception):
    def __init__(self, i, var_name, path_):
        self.message = str(path_) + ": Line {}: S011 Variable '{}' should be written in snake_case".format(i, var_name)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomDefaultArgIsMutableException(Exception):
    def __init__(self, i, path_):
        self.message = str(path_) + ": Line {}: S012 The default argument value is mutable".format(i)
        super().__init__(self.message)

    def __str__(self):
        return self.message


def files_directories_check():
    path_ = sys.argv[1]
    # path_ = "/Users/aragonerua/PycharmProjects/Static Code Analyzer/Static Code Analyzer/task/analyzer/test.txt"
    array_of_files = list()
    if os.access(path_, os.X_OK):
        array_of_all_files = os.listdir(path_)
        for s in array_of_all_files:
            if os.path.basename(s).endswith(".py") and os.path.basename(s) != "tests.py":
                array_of_files.append(path_ + "/" + str(s))
    else:
        array_of_files.append(path_)
    array_of_files.sort()
    return array_of_files


def lattice_check(line_to_test):
    comm_in_line = is_comment_in_line(line_to_test)
    if not comm_in_line:
        return line_to_test
    else:
        if line_to_test.count("#") >= 2:
            ind = line_to_test.find("#", line_to_test.rfind("'"))
            return line_to_test[:ind]
        return line_to_test[:line_to_test.rfind("#")]


def comment_getting(line_to_test):
    comm_in_line = is_comment_in_line(line_to_test)
    if not comm_in_line:
        return line_to_test
    else:
        return line_to_test[line_to_test.rfind("#"):]


def is_comment_in_line(line_to_test):
    number_of_lattices = line_to_test.count("#")
    if number_of_lattices == 0:
        return False
    elif number_of_lattices >= 1:
        if line_to_test.find('"') < line_to_test.rfind("#") < line_to_test.rfind('"') or \
                line_to_test.find("'") < line_to_test.rfind("#") < line_to_test.rfind("'"):
            return False
        else:
            return True


class OwnCodeAnalyzer:
    def __init__(self, file_path):
        self.lines_array = list()
        self.file_path = file_path
        self.errors_array = dict()
        self.full_tree = None
        self.arguments_array = list()
        self.variables_array = list()
        self.arg_mutable_lines_array = list()

    def file_to_lines(self):
        with open(os.path.abspath(self.file_path), "r") as f:
            self.lines_array = f.readlines()

    def tree_creation(self):
        full_string = ""
        for i in self.lines_array:
            full_string += i
        tree = ast.parse(full_string)
        self.full_tree = tree
        # print(ast.dump(self.full_tree))
        # print(self.full_tree)

    def tree_walk(self):
        for node in ast.walk(self.full_tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                for i in node.args.args:
                    self.arguments_array.append(i)
            if isinstance(node, ast.Assign):
                self.variables_array.append(node.targets[0])
            if isinstance(node, ast.FunctionDef):
                for item in node.args.defaults:
                    if isinstance(item, ast.List):
                        if str(astunparse.unparse(item)).strip() == "[]":
                            self.arg_mutable_lines_array.append(item.lineno)

    def len_check(self):
        for i in range(len(self.lines_array)):
            try:
                cur_line = self.lines_array[i].strip()
                if len(cur_line) > 79:
                    raise CustomLenException(i + 1, self.file_path)
            except CustomLenException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    def blank_lines_check(self):
        blank_lines_counter = 0
        number_of_line = list()
        for i in range(len(self.lines_array)):
            try:
                if self.lines_array[i] == "\n":
                    blank_lines_counter += 1
                    if blank_lines_counter >= 3:
                        number_of_line.append(i)
                else:
                    blank_lines_counter = 0
                if (i == len(self.lines_array) - 1) and len(number_of_line) != 0:
                    raise CustomMoreThanTwoBlanksException(max(number_of_line) + 2, self.file_path)
            except CustomMoreThanTwoBlanksException as err:
                if max(number_of_line) + 2 not in self.errors_array.keys():
                    self.errors_array.update({max(number_of_line) + 2: [str(err)]})
                else:
                    self.errors_array[max(number_of_line)+2].append(str(err))

    def multiply_of_four_check(self):
        number_of_iteration = 0
        for i in range(len(self.lines_array)):
            try:
                space_counter = (len(self.lines_array[i].rstrip()) - len(self.lines_array[i].rstrip().lstrip()))
                if len(self.lines_array[i]) >= 2 and i == 0:
                    if space_counter != 0:
                        raise CustomIndenFourException(i+1, self.file_path)
                elif len(self.lines_array[i]) >= 2 and len(self.lines_array[i-1]) >= 2:
                    if self.lines_array[i-1].rstrip()[-1] != ":":
                        if space_counter != 0 and space_counter % 4 != 0:
                            raise CustomIndenFourException(i+1, self.file_path)
                    else:
                        number_of_iteration += 1
                        if space_counter % 4 != 0:
                            raise CustomIndenFourException(i + 1, self.file_path)
                if len(self.lines_array[i]) == len(self.lines_array[i].lstrip()):
                    number_of_iteration = 0
            except CustomIndenFourException as err:
                if i+2 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    def unn_semicolon_check(self):
        for i in range(len(self.lines_array)):
            try:
                checked_string = lattice_check(self.lines_array[i])
                if len(checked_string) >= 2 and checked_string.rstrip()[-1] == ";":
                    raise CustomUnnSemicolonException(i+1, self.file_path)
            except CustomUnnSemicolonException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    def less_space_check(self):
        for i in range(len(self.lines_array)):
            try:
                comm_in_line = is_comment_in_line(self.lines_array[i])
                if comm_in_line:
                    checked_string = lattice_check(self.lines_array[i])
                    if len(checked_string) >= 2 and checked_string[-1:-3:-1] != "  ":
                        raise CustomLessThanTwoSpacesException(i+1, self.file_path)
            except CustomLessThanTwoSpacesException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    def todo_check(self):
        for i in range(len(self.lines_array)):
            try:
                comm_in_line = is_comment_in_line(self.lines_array[i])
                if comm_in_line:
                    checked_string = comment_getting(self.lines_array[i])
                    if ("todo" in checked_string) or ("TODO" in checked_string) or ("Todo" in checked_string):
                        raise CustomTODOFoundException(i+1, self.file_path)
            except CustomTODOFoundException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    def too_many_spaces_check(self):
        for i in range(len(self.lines_array)):
            try:
                if ("class" in self.lines_array[i]) and self.lines_array[i][0] != "#":
                    if not re.match(r"class \w+", self.lines_array[i]):
                        raise CustomTooManySpacesException(i+1, "class", self.file_path)
                elif ("def" in self.lines_array[i]) and self.lines_array[i][0] != "#":
                    # string_without_rep_whitespaces = " ".join(self.lines_array[i].split())
                    if not re.match(r" *def \w+", self.lines_array[i]):
                        raise CustomTooManySpacesException(i+1, "def", self.file_path)
            except CustomTooManySpacesException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    #TODO rewrite it using ast module
    def camel_case_check_class(self):
        for i in range(len(self.lines_array)):
            try:
                if ("class" in self.lines_array[i]) and self.lines_array[i][0] != "#":
                    string_without_rep_whitespaces = " ".join(self.lines_array[i].split())
                    class_name = ""
                    for symbol in string_without_rep_whitespaces[6:]:
                        if symbol.isalpha():
                            class_name += symbol
                        else:
                            break
                    if not re.match(r"class [A-Z]\w*[A-Z]*", string_without_rep_whitespaces):
                        raise CustomCamelCaseException(i+1, class_name, self.file_path)
            except CustomCamelCaseException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    #TODO rewrite it using ast module
    def snake_case_check_def(self):
        for i in range(len(self.lines_array)):
            try:
                if ("def" in self.lines_array[i]) and self.lines_array[i][0] != "#":
                    string_without_rep_whitespaces = " ".join(self.lines_array[i].split())
                    func_name = ""
                    for symbol in string_without_rep_whitespaces[4:]:
                        if symbol != "(":
                            func_name += symbol
                        else:
                            break
                    if not re.match(r"def _?_?[a-z]\w+_?_?", string_without_rep_whitespaces):
                        raise CustomSnakeCaseException(i+1, func_name, self.file_path)
            except CustomSnakeCaseException as err:
                if i+1 not in self.errors_array.keys():
                    self.errors_array.update({i+1: [str(err)]})
                else:
                    self.errors_array[i+1].append(str(err))

    def snake_case_check_arg(self):
        for argum in self.arguments_array:
            try:
                if not re.match(r"_?_?[a-z]+\w*?_?_?", argum.arg):
                    raise CustomArgNameSnakeCaseException(argum.lineno, argum.arg, self.file_path)
            except CustomArgNameSnakeCaseException as err:
                if argum.lineno not in self.errors_array.keys():
                    self.errors_array.update({argum.lineno: [str(err)]})
                else:
                    self.errors_array[argum.lineno].append(str(err))

    def snake_case_check_var(self):
        for var in self.variables_array:
            try:
                if (not re.match(r"[a-z]+\w*?", ast.unparse(var))) and ("CONSTANT" not in str(ast.unparse(var))):
                    raise CustomVarNameSnakeCaseException(var.lineno, ast.unparse(var), self.file_path)
            except CustomVarNameSnakeCaseException as err:
                if var.lineno not in self.errors_array.keys():
                    self.errors_array.update({var.lineno: [str(err)]})
                else:
                    self.errors_array[var.lineno].append(str(err))

    def mutable_argument_check(self):
        for error_line in self.arg_mutable_lines_array:
            try:
                raise CustomDefaultArgIsMutableException(error_line, self.file_path)
            except CustomDefaultArgIsMutableException as err:
                if error_line not in self.errors_array.keys():
                    self.errors_array.update({error_line: [str(err)]})
                else:
                    self.errors_array[error_line].append(str(err))

    def launch_all_tests(self):
        self.file_to_lines()
        self.len_check()
        self.multiply_of_four_check()
        self.unn_semicolon_check()
        self.less_space_check()
        self.todo_check()
        self.blank_lines_check()
        self.too_many_spaces_check()
        self.camel_case_check_class()
        self.snake_case_check_def()
        self.tree_creation()
        self.tree_walk()
        self.snake_case_check_arg()
        self.snake_case_check_var()
        self.mutable_argument_check()

    def dictionary_print(self):
        my_keys = list(self.errors_array.keys())
        my_keys.sort()
        sorted_dict = {i: self.errors_array[i] for i in my_keys}
        for i in sorted_dict.values():
            for j in i:
                print(j)


def main():
    # test = OwnCodeAnalyzer(input())
    result_files = files_directories_check()
    for s in result_files:
        # full_path = os.path.abspath(s)
        test = OwnCodeAnalyzer(s)
        test.launch_all_tests()
        '''
        test.file_to_lines()
        test.len_check()
        test.multiply_of_four_check()
        test.unn_semicolon_check()
        test.less_space_check()
        test.todo_check()
        test.blank_lines_check()
        test.too_many_spaces_check()
        test.camel_case_check()
        test.snake_case_check()
        '''
        test.dictionary_print()
        # my_keys = list(test.errors_array.keys())
        # my_keys.sort()
        # sorted_dict = {i: test.errors_array[i] for i in my_keys}
        # for i in sorted_dict.values():
        #     for j in i:
        #         print(j)


if __name__ == "__main__":
    main()
