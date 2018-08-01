import io
from gettext import gettext
from flask import Flask, send_file
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.sqlalchemy import SQLAlchemy
from markupsafe import Markup
from werkzeug.datastructures import FileStorage
from wtforms import ValidationError, fields
from wtforms.validators import required
from wtforms.widgets import HTMLString, html_params, FileInput

try:
    from wtforms.fields.core import _unset_value as unset_value
except ImportError:
    from wtforms.utils import unset_value

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


def build_db():
    db.drop_all()
    db.create_all()


class BlobMixin(object):
    mimetype = db.Column(db.Unicode(length=255), nullable=False)
    filename = db.Column(db.Unicode(length=255), nullable=False)
    blob = db.Column(db.LargeBinary(), nullable=False)
    size = db.Column(db.Integer, nullable=False)


class Image(db.Model, BlobMixin):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(length=255), nullable=False, unique=True)

    def __unicode__(self):
        return u"name : {name}; filename : {filename})".format(name=self.name, filename=self.filename)


class BlobUploadField(fields.StringField):

    widget = FileInput()

    def __init__(self, label=None, allowed_extensions=None, size_field=None, filename_field=None, mimetype_field=None, **kwargs):

        self.allowed_extensions = allowed_extensions
        self.size_field = size_field
        self.filename_field = filename_field
        self.mimetype_field = mimetype_field
        validators = [required()]

        super(BlobUploadField, self).__init__(label, validators, **kwargs)

    def is_file_allowed(self, filename):
        """
            Check if file extension is allowed.

            :param filename:
                File name to check
        """
        if not self.allowed_extensions:
            return True

        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in
                map(lambda x: x.lower(), self.allowed_extensions))

    def _is_uploaded_file(self, data):
        return (data and isinstance(data, FileStorage) and data.filename)

    def pre_validate(self, form):
        super(BlobUploadField, self).pre_validate(form)
        if self._is_uploaded_file(self.data) and not self.is_file_allowed(self.data.filename):
            raise ValidationError(gettext('Invalid file extension'))

    def process_formdata(self, valuelist):
        if valuelist:
            data = valuelist[0]
            self.data = data

    def populate_obj(self, obj, name):

        if self._is_uploaded_file(self.data):

            _blob = self.data.read()

            setattr(obj, name, _blob)

            if self.size_field:
                setattr(obj, self.size_field, len(_blob))

            if self.filename_field:
                setattr(obj, self.filename_field, self.data.filename)

            if self.mimetype_field:
                setattr(obj, self.mimetype_field, self.data.content_type)


class ImageView(ModelView):

    column_list = ('name', 'size', 'filename', 'mimetype', 'download')
    form_columns = ('name', 'blob')

    form_extra_fields = {'blob': BlobUploadField(
        label='File',
        allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'gif'],
        size_field='size',
        filename_field='filename',
        mimetype_field='mimetype'
    )}

    def _download_formatter(self, context, model, name):
        return Markup("<a href='{url}' target='_blank'>Download</a>".format(url=self.get_url('download_blob', id=model.id)))

    column_formatters = {
        'download': _download_formatter,
    }


# download route

@app.route("/download/<int:id>", methods=['GET'])
def download_blob(id):
    _image = Image.query.get_or_404(id)
    return send_file(
        io.BytesIO(_image.blob),
        attachment_filename=_image.filename,
        mimetype=_image.mimetype
    )

# Create admin
admin = Admin(app, name='Admin', url='/')
admin.add_view(ImageView(model=Image, session=db.session, category='Database', name='Images'))


@app.before_first_request
def first_request():
    build_db()

if __name__ == '__main__':
    app.run(debug=True, port=7777)
