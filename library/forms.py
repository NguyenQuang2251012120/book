from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CATEGORY_CHOICES, PAYMENT_METHOD_CHOICES, Book, BorrowedBook, Member


class AddMemberForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập tên thành viên"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập email thành viên"})
    )

    class Meta:
        model = Member
        fields = ["name", "email"]
        labels = {
            "name": "Họ và Tên",
            "email": "Địa chỉ Email"
        }


    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Member.objects.filter(email=email).exists():
            raise ValidationError(_("Thành viên với email đó đã có"))

        return email


class UpdateMemberForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập tên thành viên"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập email thành viên"})
    )

    class Meta:
        model = Member
        fields = ["name", "email"]
        labels = {
            "name": "Họ và Tên",
            "email": "Địa chỉ Email"
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Member.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("Thành viên với email đó đã có"))

        return email


class AddBookForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập tiêu đề sách"})
    )
    author = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập tên tác giả"})
    )

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES, widget=forms.Select(attrs={"class": "form-control form-control-lg"})
    )

    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập số lượng"})
    )

    borrowing_fee = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "Nhập giá thuê"})
    )

    class Meta:
        model = Book
        fields = ["title", "author", "category", "quantity", "borrowing_fee"]
        labels = {
            "title": "Tiêu đề",
            "author": "Tác giả",
            "category": "Danh mục",
            "quantity": "Số lượng",
            "borrowing_fee": "Giá thuê"
        }


class LendBookForm(forms.ModelForm):
    book = forms.ModelChoiceField(
        label="Book / Books",
        queryset=Book.objects.none(),  # Khởi tạo rỗng, sau này lọc dựa trên user
        empty_label=None,
        widget=forms.Select(
            attrs={"class": "form-control form-control-lg js-example-basic-multiple w-100", "multiple": "multiple"}
        ),
    )

    member = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control form-control-lg js-example-basic-single w-100"}),
    )

    return_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date", "id": "return-date"})
    )

    fine = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "Enter Fine"})
    )

    class Meta:
        model = BorrowedBook
        fields = ["book", "member", "return_date", "fine"]
        labels = {
            "book": "Sách",
            "member": "Thành viên",
            "return_date": "Ngày trả",
            "fine": "Giá phạt"
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Nhận user từ View
        super().__init__(*args, **kwargs)
        if user:
            # Lọc danh sách sách
            self.fields['book'].queryset = Book.objects.filter(quantity__gt=0, librarian=user)
            # Lọc danh sách thành viên
            self.fields['member'].queryset = Member.objects.filter(librarian=user)



class LendMemberBookForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filter danh sách sách theo librarian đang đăng nhập nếu cần:
        if self.user:
            self.fields['book'].queryset = Book.objects.filter(quantity__gt=0, librarian=self.user)

    book = forms.ModelChoiceField(
        label="Book / Books",
        queryset=Book.objects.filter(quantity__gt=0),  # sẽ được override trong __init__
        empty_label=None,
        widget=forms.Select(
            attrs={"class": "form-control form-control-lg js-example-basic-multiple w-100", "multiple": "multiple"}
        ),
    )

    member = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control form-control-lg js-example-basic-single w-100"}),
    )

    return_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date", "id": "return-date"})
    )

    fine = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "Enter Fine"})
    )

    class Meta:
        model = BorrowedBook
        fields = ["book", "member", "return_date", "fine"]
        labels = {
            "book": "Sách",
            "member": "Thành viên",
            "return_date": "Ngày trả",
            "fine": "Giá phạt"
        }


class UpdateBorrowedBookForm(forms.ModelForm):
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date", "id": "return-date"})
    )

    fine = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "Enter Fine"})
    )

    class Meta:
        model = BorrowedBook
        fields = ["return_date", "fine"]
        label = {
            "return_date": "Ngày trả",
            "fine": "Giá phạt"
        }


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES, widget=forms.Select(attrs={"class": "form-control form-control-lg"})
    )

    class Meta:
        fields = ["payment_method"]
        label = {
            "payment_method": "Hình thức trả tiền"
        }
