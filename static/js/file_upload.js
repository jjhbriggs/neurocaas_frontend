
/*
*   FileUpload Object.
*   % Drag & Drop, Browser direct upload to s3, Resume uploading if net failed, Show uploading progress bar
*
*   Created by Johan on 2/18/2020
*/

var FileUpload = function(){}

FileUpload.prototype ={
    form_id: null,
    dropArea: null,
    uploadProgress: [],
    uploadFileSize: [],
    progressBar: null,
    id1: null,
    id2: null,
    file: null,
    bucket: null,
    subfolder: null,
    fileKey: null,
    buffer: null,
    startTime: new Date(),
    partNum: 0,
    defaultSize: 1024 * 1024 * 5,
    partSize: 1024 * 1024 * 5,
    numPartsLeft: null,
    maxUploadTries: 3,
    multiPartParams: null,
    multipartMap: { Parts: []},
    s3: null,
    status: false,
    file_tag_id: null,
    file_count: 0,
    uploaded_count: 0,
    trigger: null,
    contentious: false,
    current_file_id: 0,
    files: [],
    init: function(form_id, id1, id2, bucket, subfolder, file_tag_id, trigger=null, contentious=false){
        this.form_id = form_id;
        this.id1 = id1;
        this.id2 = id2;
        this.bucket = bucket;
        this.subfolder = subfolder;
        this.file_tag_id = file_tag_id;
        this.dropArea = document.getElementById(this.form_id)
        var sender = this;  // this object
        this.uploadProgress = []
        this.progressBar = document.querySelector('#' + this.form_id + ' .progress-bar')
        this.trigger = trigger;
        this.contentious = contentious;

        /* S3 bucket options */
            AWS.config.apiVersions = {
                s3: '2006-03-01'
            };

            //  init s3

            this.s3 = new AWS.S3({
                accessKeyId: atob(atob(sender.id1)),
                secretAccessKey: atob(atob(sender.id2)),
            });

            // function completeMultipartUpload
            completeMultipartUpload = function(_this, s3, doneParams) {
                s3.completeMultipartUpload(doneParams, function(err, data) {
                    if (err) {
                      console.log("An error occurred while completing the multipart upload");
                      console.log(err);
                    } else {
                        var delta = (new Date() - sender.startTime) / 1000;
                        //alert("Finished loading!");
                        console.log('Completed upload in', delta, 'seconds');
                        console.log('Final upload data:', data);
                        _this.current_file_id++;
                        if (_this.current_file_id < _this.files.length)
                            uploadFile(_this, _this.files[_this.current_file_id]);
                        else{
                            if (_this.trigger) _this.trigger();
                        }
                    }
                });
            }

            // function uploadPart
            uploadPart = function(_this, s3, multipart, partParams, tryNum) {
                var tryNum = tryNum || 1;
                s3.uploadPart(partParams, function(multiErr, mData) {
                    if (multiErr){
                        console.log('multiErr, upload part error:', multiErr);
                        if (tryNum < _this.maxUploadTries) {
                            console.log('Retrying upload of part: #', partParams.PartNumber)
                            uploadPart(_this, s3, multipart, partParams, tryNum + 1);
                        } else {
                            console.log('Failed uploading part: #', partParams.PartNumber)
                        }
                        return;
                    }
                    _this.multipartMap.Parts[this.request.params.PartNumber - 1] = {
                        ETag: mData.ETag,
                        PartNumber: Number(this.request.params.PartNumber)
                    };
                    console.log("Completed part", this.request.params.PartNumber);
                    console.log('mData', mData);
                    updateProgress(_this);
                    if (--_this.numPartsLeft > 0) return; // complete only when all parts uploaded

                    var doneParams = {
                        Bucket: _this.bucket,
                        Key: _this.subfolder + "/" + _this.fileKey,
                        MultipartUpload: _this.multipartMap,
                        UploadId: multipart.UploadId
                    };

                    console.log("Completing upload...");
                    completeMultipartUpload(_this, s3, doneParams);
                    updateProgress(_this);
                    //_this.status = true;
                    $('#' + _this.form_id + ' p').html("Uploading was finished!");
                    // $('#' + _this.file_tag_id).val(_this.fileKey);
                });
            }

        /* End S3 bucket options */

        // Prevent default drag behaviors
        ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.preventDefaults, false)
            document.body.addEventListener(eventName, this.preventDefaults, false)
        })

        // Highlight drop area when item is dragged over it
        ;['dragenter', 'dragover'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.highlight, false)
        })

        // Unhighlight drop area when item is canceled.
        ;['dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.unhighlight, false)
        })

        // On Click event when user click drop area
        this.dropArea.addEventListener('click', function(e){
            if ( !sender.contentious && sender.status ) return;
            $( '#' + sender.form_id + ' .fileElem' ).trigger('click');
        }, false);

        // preview file after drop a file
        var previewFile = function(file) {
            console.log(file.name)
            let reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onloadend = function() {
                let label = document.createElement('label');
                label.innerText = file.name;
                console.log(document.querySelector('#' + sender.form_id + ' .gallery'));
                document.querySelector('#' + sender.form_id + ' .gallery').appendChild(label)
            }
        }

        // init uploading progress bar
        var initializeProgress = function(Files) {
            sender.progressBar.value = 0
            sender.uploadProgress = [];
            sender.uploadFileSize = [];

            for(let i = 0; i < Files.length; i++) {
                sender.uploadProgress.push(0)
                sender.uploadFileSize.push(Files[i].size);
            }

            $('#' + sender.form_id + " .gallery").html("");
        }

        // update uploading status in progress bar
        var updateProgress = function(_this) {
            var percent = (_this.partNum - _this.numPartsLeft)/_this.partNum * 100;
            _this.uploadProgress[_this.current_file_id] = percent;

            // calculate total percentage
            var percent = 0, total_size = 0, current_size = 0;
            for ( var i = 0 ; i < _this.uploadFileSize.length; i++ ){
                total_size += _this.uploadFileSize[i];
                current_size += _this.uploadFileSize[i] * _this.uploadProgress[i];
            }

            percent = current_size/total_size;

            console.log('update', _this.partNum, _this.numPartsLeft, percent);

            _this.progressBar.value = percent;
        };

        // upload file to s3

        var uploadFile = function(_this, file) {
            const reader = new FileReader();
            reader.readAsArrayBuffer(file)

            var params = {
                Bucket: sender.bucket,
                Key: sender.subfolder + "/" + file.name,
                Body: file
            };

            /* Disabled the upload once for demo */
            /*
            sender.s3.upload(params, function(err, data) {
                if (err) {
                    console.log(err, err.stack);
                } else {
                    console.log(data.Key + ' successfully uploaded to' + data.Location);
                    var percent = ++sender.uploaded_count/sender.file_count * 100;
                    sender.progressBar.value = percent;
                    if (percent >= 100) {
                        sender.status = true;
                        $('#' + sender.form_id + ' p').html("Uploading was finished!");
                        if (sender.trigger) sender.trigger();
                    }
                }
            });*/

            /* Disabled the multipart upload for demo */
            reader.onloadend = function onloadend(){
                console.log('on_loaded');
                _this.buffer = reader.result;
                _this.startTime = new Date();
                _this.partNum = 0;
                _this.fileKey = file.name
                _this.partSize = file.size / 20 > _this.defaultSize ? file.size / 20 : _this.defaultSize;
                _this.numPartsLeft = Math.floor(file.size / _this.partSize);
                file.size - _this.partSize * _this.numPartsLeft > _this.defaultSize ? _this.numPartsLeft++ : null;

                _this.maxUploadTries = 3;
                _this.multiPartParams = {
                    Bucket: _this.bucket,
                    Key: _this.subfolder + "/" + _this.fileKey,
                    ContentType: file.type
                };
                _this.multipartMap = {
                    Parts: []
                };

                console.log("Creating multipart upload for:", _this.fileKey);
                _this.s3.createMultipartUpload(_this.multiPartParams, function(mpErr, multipart){
                    if (mpErr) { console.log('Error!', mpErr); return; }
                    console.log("Got upload ID", multipart.UploadId);

                    // Grab each partSize chunk and upload it as a part
                    for (var rangeStart = 0; rangeStart < _this.buffer.byteLength; rangeStart += _this.partSize) {
                        _this.partNum++;
                        var end = Math.min(rangeStart + _this.partSize, _this.buffer.byteLength);
                        if ( _this.buffer.byteLength - end < _this.partSize ) end = _this.buffer.byteLength;

                        console.log(end - rangeStart, _this.partSize)

                        var partParams = {
                              Body: _this.buffer.slice(rangeStart, end),
                              Bucket: _this.bucket,
                              Key: _this.subfolder + "/" + _this.fileKey,
                              PartNumber: String(_this.partNum),
                              UploadId: multipart.UploadId
                            };

                        // Send a single part
                        console.log('Uploading part: #', partParams.PartNumber, ', Range start:', rangeStart);
                        //updateProgress(sender);
                        uploadPart(_this, _this.s3, multipart, partParams);
                        if (end == _this.buffer.byteLength) break;
                    }
                });
            }
        }

        // Handle files of file tag
        var handleFiles = function(_this, files) {
            if (!_this.bucket){
                alert("Select a bucket for uploading");
                return;
            }
            files = [...files];
            _this.files = files;
            initializeProgress(files)
            _this.current_file_id = 0;
            uploadFile(_this, files[_this.current_file_id]);
            files.forEach(previewFile)
        }

        // Handle dropped files
        this.dropArea.addEventListener('drop', function(e){
            if (!sender.contentious && sender.status) return;
            var dt = e.dataTransfer
            var files = dt.files
            handleFiles(sender, files)
        }, false);

        // add eventlistener when the file tag is changed
        document.querySelector('#' + this.form_id + ' .fileElem').addEventListener('change', function(e){
            var files = e.target.files;
            handleFiles(sender, files);
        }, false);
    },

    preventDefaults (e) {
        e.preventDefault()
        e.stopPropagation()
    },

    highlight(e) {
        this.classList.add('highlight')
    },

    unhighlight(e) {
        this.classList.remove('active')
    },
    clear_status: function(){
        this.progressBar.value = 0;
        $('#' + this.form_id + ' p').html("Drag & Drop or Click!");
        $('#' + this.form_id + ' .gallery').html("");        
    },
    set_bucket(bucket){
        console.log(this.bucket);
        this.bucket = bucket;
        console.log(this.bucket);
        console.log("--------------------------");
    }
}