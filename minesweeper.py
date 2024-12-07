
import itertools
import random


class Minesweeper():


    def __init__(self, height=8, width=8, mines=8):

        # Set chiều cao, chiều rộng và số mìn
        self.height = height
        self.width = width
        self.mines = set()

        #khởi tạo
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # random mìn
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # mìn đã tìm được
        self.mines_found = set()

    def print(self):
        """
        kiểm tra vị trị mìn
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Số lượng mìn ở gần
        """

        
        count = 0

        # vòng lặp các ô ở gần ô cần kiểm tra
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # bỏ qua ô đang kiểm tra 
                if (i, j) == cell:
                    continue

                # cập nhật nếu tìm thấy mìn
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Kiểm tra nếu tất cả mìn đã được đánh dấu
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Các thông tin về màn chơi
    Mỗi câu bao gồm một tập hợp các ô bảng,
    và số lượng của các ô là mìn.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Trả về tập hợp tất cả các ô trong self.cells đã biết là mìn.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Trả về tập hợp tất cả các ô trong self.cells đã biết an toàn.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Cập nhật tri thức khi biết một ô là mìn
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Cập nhật tri thức khi biết một ô an toàn
        """
        if cell in self.cells:
            self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper AI
    """

    def __init__(self, height=8, width=8):

        # Set chiều cao và chiều rộng
        self.height = height
        self.width = width

        # Theo dõi các ô nào đã được mở
        self.moves_made = set()

        # Theo dõi các ô được biết là an toàn hoặc mìn
        self.mines = set()
        self.safes = set()

        # Danh sách thông tin về trò chơi được biết là đúng
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Đánh dấu một ô là mìn và cập nhật tất cả các kiến thức
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Đánh dấu một ô là an toàn và cập nhật tất cả các kiến thức
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def nearby_cells(self, cell):
        cells = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    cells.add((i, j))

        return cells

    def add_knowledge(self, cell, count):
        """
        Được gọi khi một ô được mở và kiểm tra xem có bao nhiêu mìn xung quanh
        Chức năng:
        1) Đánh dấu ô là đã mở
        2) Đánh dấu ô là an toàn
        3) Thêm một câu mới vào cơ sở kiến thức của AI
        dựa trên giá trị của `cell` và` Count`
        4) Đánh dấu bất kỳ ô bổ sung nào là an toàn hoặc là mỏ
        Nếu nó có thể được kết luận dựa trên cơ sở kiến thức của AI
        5) Thêm bất kỳ câu mới nào vào cơ sở kiến thức của AI
        Nếu chúng có thể được suy ra từ kiến thức hiện có
        """

        # đánh dấu ô đã mở
        self.moves_made.add(cell)

        # đánh dấu ô an toàn
        if cell not in self.safes:
            self.mark_safe(cell)

        # số ô ở gần
        nearby = self.nearby_cells(cell)

        # bỏ đi những ô đã được mở và những ô an toàn
        nearby -= self.safes | self.moves_made

        new_sentence = Sentence(nearby, count)

        self.knowledge.append(new_sentence)

        new_safes = set()
        new_mines = set()

        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
            else:
                tmp_new_safes = sentence.known_safes()
                tmp_new_mines = sentence.known_mines()

                if type(tmp_new_safes) is set:
                    new_safes |= tmp_new_safes

                if type(tmp_new_mines) is set:
                    new_mines |= tmp_new_mines

        for safe in new_safes:
            self.mark_safe(safe)

        for mine in new_mines:
            self.mark_mine(mine)

        prev_sentence = new_sentence

        new_inferences = []

        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

            elif prev_sentence == sentence:
                break
            elif prev_sentence.cells <= sentence.cells:
                inf_cells = sentence.cells - prev_sentence.cells
                inf_count = sentence.count - prev_sentence.count

                new_inferences.append(Sentence(inf_cells, inf_count))

            prev_sentence = sentence

        self.knowledge += new_inferences

    def make_safe_move(self):
        """
        Trả về một ô an toàn để chọn trên bảng.
        Việc di chuyển phải được biết là an toàn và không phải ô đã mở
        Hàm này có thể sử dụng kiến thức trong self.mines, self.safes
        và self.moves_made, nhưng không được sửa đổi bất kỳ giá trị nào trong số đó.
        """

        safe_moves = self.safes.copy()

        safe_moves -= self.moves_made

        if len(safe_moves) == 0:
            return None

        return safe_moves.pop()

    def make_random_move(self):
        """
        Trả lại một nước đi random
        chọn các ô có các yếu tố sau:
            1) chưa được mở
            2) chưa biết đó là mìn
        """

        def get_random_cell():
            return (random.randrange(self.height),
                    random.randrange(self.height))

        # Nếu không có nước đi random, trả về None
        # width=8 * height=8 - mines=8 -> 56
        if len(self.moves_made) == 56:
            return None

        random_move = get_random_cell()

        not_safe_moves = self.moves_made | self.mines

        while random_move in not_safe_moves:
            random_move = get_random_cell()

        return random_move
