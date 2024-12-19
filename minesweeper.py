
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

    def __init__(self, height=8, width=8, mine=8):

        # Set chiều cao, chiều rộng và số mìn
        self.height = height
        self.width = width
        self.mine = mine
        # Theo dõi các ô nào đã được mở
        self.moves_made = set()

        # Theo dõi các ô được biết là an toàn hoặc mìn
        self.mines = set()
        self.safes = set()

        # Danh sách thông tin về trò chơi được biết là đúng
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Đánh dấu một ô là mìn.
        """
        if cell not in self.mines:
            self.mines.add(cell)
            self.knowledge = [
                Sentence(sentence.cells - {cell}, sentence.count - 1)
                if cell in sentence.cells else sentence
                for sentence in self.knowledge
            ]

    def mark_safe(self, cell):
        """
        Đánh dấu một ô là an toàn.
        """
        if cell not in self.safes:
            self.safes.add(cell)
            self.knowledge = [
                Sentence(sentence.cells - {cell}, sentence.count)
                if cell in sentence.cells else sentence
                for sentence in self.knowledge
            ]


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
            if safe not in self.safes:
                self.mark_safe(safe)

        for mine in new_mines:
            if mine not in self.mines:
                self.mark_mine(mine)

        prev_sentence = new_sentence

        new_inferences = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 == sentence2 or len(sentence1.cells) == 0 or len(sentence2.cells) == 0:
                    continue

                # Nếu sentence1 là tập con của sentence2
                if sentence1.cells <= sentence2.cells:
                    inferred_cells = sentence2.cells - sentence1.cells
                    inferred_count = sentence2.count - sentence1.count
                    new_inference = Sentence(inferred_cells, inferred_count)

                    # Kiểm tra nếu suy luận mới chưa tồn tại
                    if new_inference not in self.knowledge and len(new_inference.cells) > 0:
                        new_inferences.append(new_inference)

        self.knowledge.extend(new_inferences)

        
        

    def make_safe_move(self):
        """
        Trả về một ô an toàn để chọn trên bảng.
        Việc di chuyển phải được biết là an toàn và không phải ô đã mở
        Hàm này có thể sử dụng kiến thức trong self.mines, self.safes
        và self.moves_made, nhưng không được sửa đổi bất kỳ giá trị nào trong số đó.
        """

        safe_moves = self.safes - self.moves_made
        if safe_moves:
            return safe_moves.pop()

        # Nếu không có nước đi an toàn ngay lập tức, thử kiểm tra thêm tri thức
        for sentence in self.knowledge:
            inferred_safes = sentence.known_safes()
            if inferred_safes:
                return next(iter(inferred_safes - self.moves_made), None)

        return None

    def make_random_move(self):
        """
        Trả về một nước đi ngẫu nhiên.
        """
        possible_moves = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        return random.choice(possible_moves) if possible_moves else None

