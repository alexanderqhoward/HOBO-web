import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import img2pdf
from PIL import Image

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 获取当前文件所在的目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 创建 uploads 文件夹的完整路径
uploads_folder = os.path.join(current_dir, 'uploads')
# 确保 uploads 文件夹存在
if not os.path.exists(uploads_folder):
    os.makedirs(uploads_folder)


app.config['UPLOAD_FOLDER'] = uploads_folder

@app.route('/', methods=['GET'])
def index():
    html_code = '''
    <!DOCTYPE html>
    <html>
      <head>
        <title>PNG to PDF Converter</title>
      </head>
      <body>
        <h1>PNG to PDF Converter</h1>
        <form action="/convert" method="POST" enctype="multipart/form-data">
          <input type="file" name="file">
          <input type="submit" value="Convert">
        </form>
      </body>
    </html>
    '''
    return html_code

@app.route('/convert', methods=['POST'])
def convert():
    # 检查文件是否被上传
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']

    # 检查文件名是否有效
    if file.filename == '':
        return 'Invalid file name', 400

    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return 'Invalid file type', 400

    # 确保上传文件的文件名不包含任何路径信息
    filename = secure_filename(file.filename)

    # 将上传的文件保存到本地
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 使用PIL库打开图片文件
    try:
        with Image.open(file_path) as img:
            # 将图片转换为PDF
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.pdf")
            img.save(pdf_path, "PDF")
    except Exception as e:
        return f"Failed to convert image: {str(e)}", 500

    # 返回转换后的PDF文件供下载
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug = True)