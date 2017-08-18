import StringIO
from django.http import HttpResponse

__author__ = ''


def download_order_files(order):
    contract = order
    if contract.state.name == 'Offen':
        contract.state = State.objects.get(name='In Bearbeitung')
        contract.date_downloaded = datetime.now()
        contract.user_downloaded = request.user
        contract.save()

    filenames = []
    if contract.file:
        filenames.append(contract.file.path)
    if contract.file2:
        filenames.append(contract.file2.path)
    if contract.file3:
        filenames.append(contract.file3.path)
    if contract.file4:
        filenames.append(contract.file4.path)
    if contract.logo and contract.contact.logo:
        filenames.append(contract.contact.logo.path)
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = str(contract.number)
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type

    resp = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp
