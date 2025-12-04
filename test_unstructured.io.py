from unstructured.partition.pdf import partition_pdf

print("--- Đang xử lý PDF... ---")

elements = partition_pdf(filename="Scanned.pdf", strategy="auto", languages=["vie"])

print(f"\nĐã xong! Tìm thấy {len(elements)} phần tử (elements).\n")
print("--- KẾT QUẢ ---")

for el in elements:
    print(f"[{el.category}]: {el.text}")
    print("-" * 30)