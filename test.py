from reader import get_file_list, read_text_file
from preprocessing import preprocessing
from extractor import Extractor
from textrank import TextRankModel

# file_list = get_file_list('datasets/data_original_files0-9999')
# # text = read_text_file(file_list[0][1])

# number = 9000

# a = read_text_file(file_list[number][0])
# c = read_text_file(file_list[number][1])

# print(file_list[0][1])
# print('--------------------------------------------------------------------------')
# print(c)
# print('--------------------------------------------------------------------------')
# print(preprocessing(c))

# extractor = Extractor()

# a_ners, a_candidates = extractor.extract(a)
# c_ners, c_candidates = extractor.extract(c)
# doc = a_candidates + c_candidates
# ners = (a_ners, c_ners)

tr = TextRankModel()

# print('Named entity in about:', ners[0])
# print('Named entity in content:', ners[1])

# print('Keywords:')
# keywords = tr.get_keywords(doc, number=20, window_size=4)
# for kw, point in keywords:
#     print(kw, '-', point)


text = 'Vv phản ánh của Báo Đời sống & Tiêu dùng liên quan đến các dấu hiệu vi phạm của HKD Sắc Mộc Thiên. CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM. Độc lập - Tự do – Hạnh phúc. Thành phố Hồ Chí Minh, ngày tháng năm 2018 .\
 Kính gửi: Ủy ban nhân dân quận Gò Vấp. \
 Sở Y tế nhận được mail của Cơ quan đại diện tại Thành phố Hồ Chí Minh Báo Đời sống & Tiêu dùng về việc phản ánh của bạn đọc tại Thành phố Hồ Chí Minh \
 xuất hiện một số sản phẩm chăm sóc sức khỏe nhãn hiệu Sắc Mộc Thiên (địa chỉ trên sản phẩm: 28/10 Phạm Văn Chiêu, Phường 8, quận Gò Vấp) có dấu hiệu vi phạm quy định trong lĩnh vực Y tế. \
 Được biết, ngay sau khi Ủy ban nhân dân quận Gò Vấp xác minh và trả lời báo chí về việc không tồn tại hoạt động của Hộ kinh doanh Sắc Mộc Thiên \
do Ông Vũ Duy Mạnh làm đại diện tại địa chỉ số 28/10 Phạm Văn Chiêu, Phường 8, quận Gò Vấp thì Ông Mạnh chấm dứt hoạt động Hộ kinh doanh tại địa chỉ trên \
và thành lập Hộ kinh doanh Sắc Mộc Thiên tại địa chỉ 25/8/4 Lý Thường Kiệt, Phường 4, quận Gò Vấp. \
 Sở Y tế đề nghị Ủy ban nhân dân quận Gò Vấp tiếp tục giám sát hoạt động, kiểm tra, xử lý đối với Hộ kinh doanh Sắc Mộc Thiên \
     tại địa chỉ 25/8/4 Lý Thường Kiệt, Phường 4, quận Gò Vấp do Ông Vũ Duy Mạnh làm đại diện nếu có vi phạm, đồng thời phản hồi cho Sở Y tế và cơ quan báo chí được biết./.'
ext = Extractor()

print('lt:')
print(ext.get_long_tokens(text))
print('Start...')

ners, new_text = ext.merge_name_entities(text)
print('ners:', ners)
keywords = tr.get_keywords(new_text, number=20, window_size=3)
for kw, point in keywords:
    print(kw, '-', point)
