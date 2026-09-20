# Mini House Price Prediction

Mở terminal PowerShell tại thư mục gốc của dự án và chạy:

```powershell
cd "C:\Users\OWNER\OneDrive - National Economics University\Documents\mini house price prediction"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\backend\.venv\Scripts\Activate.ps1"
cd ".\lab_01"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Nếu không muốn kích hoạt môi trường ảo, dùng trực tiếp:

```powershell
cd "C:\Users\OWNER\OneDrive - National Economics University\Documents\mini house price prediction\lab_01"
& "..\backend\.venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Sau khi server chạy, mở:

- Swagger API: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Frontend tĩnh: <http://127.0.0.1:8000/static/index.html>

## Chạy Item Manager

Sau khi server đã chạy, mở đường dẫn sau trên trình duyệt:

<http://127.0.0.1:8000/static/index.html>

Tại giao diện **Item Management Dashboard**, bạn có thể:

- Thêm item bằng cách nhập tên, giá và trạng thái tồn kho rồi bấm **Add Item**.
- Bấm **Edit** để cập nhật item.
- Bấm **Delete** để xóa item.
- Tạo item có tên trùng để kiểm tra lỗi `409 Conflict`.

### Thử nhanh trong Swagger

1. Dùng `POST /items` để tạo một vài item.
2. Dùng `PATCH /items/{item_id}` để sửa riêng `name`, `price` hoặc `in_stock`.
3. Dùng `GET /items` để thử lọc, tìm kiếm, sắp xếp và phân trang.
4. Tạo tên trùng để kiểm tra lỗi `409 Conflict`.
5. Dùng `POST /predict/house-price` với body:

```json
{
	"area_sqm": 50,
	"bedrooms": 2,
	"distance_to_center_km": 3
}
```
