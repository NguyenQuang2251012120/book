from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from users.models import AbstractBaseModel

STATUS_CHOICES = (
    ("available", "Available"),
    ("not-available", "Not-Available"),
)

CATEGORY_CHOICES = (
    ("adventure", "Adventure - Phiêu lưu"),
    ("art", "Art/Photography - Nghệ thuật/Nhiếp ảnh"),
    ("biography", "Biography - Tiểu sử"),
    ("children", "Children - Thiếu nhi"),
    ("cooking", "Cooking/Culinary - Ẩm thực"),
    ("diy", "DIY/Crafts - Tự làm/Thủ công"),
    ("drama", "Drama - Kịch"),
    ("economics", "Economics - Kinh tế"),
    ("education", "Education/Academic - Giáo dục/Học thuật"),
    ("environmental", "Environmental - Môi trường"),
    ("fantasy", "Fantasy - Kỳ ảo"),
    ("fashion", "Fashion - Thời trang"),
    ("fiction", "Fiction - Tiểu thuyết"),
    ("gardening", "Gardening - Làm vườn"),
    ("graphic-novels", "Graphic Novels/Comics - Truyện tranh"),
    ("health", "Health & Wellness - Sức khỏe"),
    ("history", "History - Lịch sử"),
    ("horror", "Horror - Kinh dị"),
    ("humor", "Humor - Hài hước"),
    ("legal", "Legal - Pháp luật"),
    ("memoirs", "Memoirs - Hồi ký"),
    ("mystery", "Mystery/Crime - Trinh thám"),
    ("music", "Music - Âm nhạc"),
    ("non-fiction", "Non-Fiction - Phi hư cấu"),
    ("other", "Other - Khác"),
    ("pets", "Pets/Animals - Thú cưng/Động vật"),
    ("philosophy", "Philosophy - Triết học"),
    ("poetry", "Poetry - Thơ"),
    ("psychology", "Psychology - Tâm lý học"),
    ("religion", "Religion - Tôn giáo"),
    ("romance", "Romance - Lãng mạn"),
    ("science", "Science - Khoa học"),
    ("sci-fi", "Science Fiction - Khoa học viễn tưởng"),
    ("self-help", "Self-Help - Phát triển bản thân"),
    ("spirituality", "Spirituality - Tâm linh"),
    ("sports", "Sports - Thể thao"),
    ("technology", "Technology - Công nghệ"),
    ("thriller", "Thriller/Suspense - Giật gân"),
    ("travel", "Travel - Du lịch"),
    ("war", "War/Military - Chiến tranh/Quân sự"),
)



PAYMENT_METHOD_CHOICES = (
    ("cash", "Tiền mặt"),
    ("momo", "Momo"),
    ("card", "Thẻ ngân hàng"),
    ("zalopay", "Zalo Pay"),

)


class Member(AbstractBaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    amount_due = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00), MaxValueValidator(500.00)]
    )
    librarian = models.ForeignKey('users.Librarian', on_delete=models.CASCADE, related_name='members')

    def __str__(self):
        return f"{self.name}"

    def calculate_amount_due(self):
        borrowed_books = self.borrowed_books.all()
        amount = 0
        for book in borrowed_books:
            if book.return_date < timezone.now().date() and not book.returned:
                amount += book.fine
        return amount

    def save(self, *args, **kwargs):
        if not self.librarian:
            raise ValueError("Each member must be associated with a librarian.")
        super().save(*args, **kwargs)


class Book(AbstractBaseModel):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    borrowing_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=1.00, validators=[MinValueValidator(1.00)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    librarian = models.ForeignKey('users.Librarian', on_delete=models.CASCADE, related_name="books")  # Thêm trường này

    def __str__(self):
        return f"{self.title} by {self.author}"

class BorrowedBook(AbstractBaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="borrowed_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowed_books")
    return_date = models.DateField()
    returned = models.BooleanField(default=False)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])

    def __str__(self):
        return f"{self.member.name} borrowed {self.book.title} on {self.created_at}"

    def save(self, *args, **kwargs):
        if not self.member.librarian == self.book.librarian:
            raise ValueError("A member can only borrow books from their assigned librarian.")
        super().save(*args, **kwargs)




class Transaction(AbstractBaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"{self.member.name} paid {self.amount} via {self.payment_method}"

    def save(self, *args, **kwargs):
        if not self.member.librarian == self.member.librarian:
            raise ValueError("A transaction can only belong to a member associated with the librarian.")
        super().save(*args, **kwargs)
