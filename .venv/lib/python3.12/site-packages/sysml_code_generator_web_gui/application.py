import os
from base64 import b64encode
from io import BytesIO

from flask import Flask, render_template, request
from sysml_code_generator.code_generator import CodeGenerator
from zipfile import ZipFile

basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, 'templates')
public_dir = os.path.join(basedir, 'public')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_url_path='',
    static_folder=public_dir,
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/example.html')
def example():
    return render_template('example.html')


@app.route('/api.html')
def api():
    return render_template('api.html')


def handle_result(result):
    generated_files = []
    memory_file = BytesIO()

    with ZipFile(memory_file, 'w') as zf:
        for result_file in result.files:
            generated_files.append({
                "data": result_file.content,
                "name": result_file.filename,
            })

            zf.writestr(result_file.filename, result_file.content)

        zf.close()
        memory_file.seek(0)
        zip_base64 = b64encode(memory_file.read()).decode("utf-8")

        return render_template(
            template_name_or_list="result.html",
            generated_files=generated_files,
            zip_base64=zip_base64,
        )


@app.route('/generate-from-json', methods=['POST'])
def handle_generate_from_json():
    qualified_name = request.form.get('qualified_name')
    generator_type = request.form.get('generator')
    file = request.files.get("file")

    if qualified_name is None:
        return 'qualified name missing in request', 400

    if generator_type is None:
        return 'generator_type name missing in request', 400

    if file is None:
        return 'file missing in request', 400

    generated_files = []

    code_generator = CodeGenerator()

    result = code_generator.generate_from_json_stream(
        json_data=file.stream,
        element_name=qualified_name,
        generator_type=generator_type,
    )

    memory_file = BytesIO()

    with ZipFile(memory_file, 'w') as zf:
        for result_file in result.files:
            generated_files.append({
                "data": result_file.content,
                "name": result_file.filename,
            })

            zf.writestr(result_file.filename, result_file.content)

        zf.close()
        memory_file.seek(0)
        zip_base64 = b64encode(memory_file.read()).decode("utf-8")

        return render_template(
            template_name_or_list="result.html",
            generated_files=generated_files,
            zip_base64=zip_base64,
        )


@app.route('/generate-from-api', methods=['POST'])
def handle_generate_from_api():
    qualified_name = request.form.get('qualified_name')
    generator_type = request.form.get('generator')
    api_base_url = request.form.get("api_base_url")
    api_project = request.form.get("api_project")

    if qualified_name is None:
        return 'qualified name missing in request', 400

    if generator_type is None:
        return 'generator_type name missing in request', 400


    if api_base_url is None:
        return 'api_base_url name missing in request', 400

    if api_project is None:
        return 'api_project name missing in request', 400

    code_generator = CodeGenerator()

    result = code_generator.generate_from_api_endpoint(
        api_base_url=api_base_url,
        project_name=api_project,
        element_name=qualified_name,
        generator_type=generator_type,
        verify_ssl=False,
    )

    return handle_result(result)


def main():
    app.run(
        host="0.0.0.0",
        debug=True,
    )


if __name__ == '__main__':
    main()
