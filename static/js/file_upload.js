
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

    init: function(form_id, id1, id2, bucket, subfolder, file_tag_id){
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
            completeMultipartUpload = function(s3, doneParams) {
                s3.completeMultipartUpload(doneParams, function(err, data) {
                    if (err) {
                      console.log("An error occurred while completing the multipart upload");
                      console.log(err);
                    } else {
                      var delta = (new Date() - sender.startTime) / 1000;
                      //alert("Finished loading!");
                      console.log('Completed upload in', delta, 'seconds');
                      console.log('Final upload data:', data);
                    }
                });
            }

            // function uploadPart
            uploadPart = function(_this, s3, multipart, partParams, tryNum) {
                var tryNum = tryNum || 1;
                s3.uploadPart(partParams, function(multiErr, mData) {
                    if (multiErr){
                        console.log('multiErr, upload part error:', multiErr);
                        if (tryNum < maxUploadTries) {
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
                    completeMultipartUpload(s3, doneParams);
                    updateProgress(_this);
                    _this.status = true;
                    $('#' + _this.form_id + ' p').html("Uploading was finished!");
                    $("#upload").attr("disabled", false);
                    $('#' + _this.file_tag_id).val(_this.fileKey);
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
            if (sender.status) return;
            $('#' + sender.form_id + ' .fileElem').trigger('click');
        }, false);

        // preview file after drop a file
        var previewFile = function(file) {
            let reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onloadend = function() {
                let label = document.createElement('lable');
                label.innerText = file.name;
                console.log(document.querySelector('#' + sender.form_id + ' .gallery'));
                document.querySelector('#' + sender.form_id + ' .gallery').appendChild(label)
            }
        }

        // init uploading progress bar
        var initializeProgress = function(numFiles) {
            sender.progressBar.value = 0
            sender.uploadProgress = []

            for(let i = numFiles; i > 0; i--) {
                sender.uploadProgress.push(0)
            }
            $('#' + sender.form_id + " .gallery").html("");
        }

        // update uploading status in progress bar
        var updateProgress = function(_this) {
            var percent = (_this.partNum - _this.numPartsLeft)/_this.partNum * 100;
            console.log('update', _this.partNum, _this.numPartsLeft, percent)
            _this.progressBar.value = percent;
        };

        // upload file to s3

        var uploadFile = function(file, i) {
            const reader = new FileReader();
            reader.readAsArrayBuffer(file)

            reader.onloadend = function onloadend(){
                console.log('on_loaded');
                sender.buffer = reader.result;
                sender.startTime = new Date();
                sender.partNum = 0;
                sender.fileKey = file.name
                sender.partSize = file.size / 20 > sender.defaultSize ? file.size / 20 : sender.defaultSize;
                sender.numPartsLeft = Math.ceil(file.size / sender.partSize);
                sender.maxUploadTries = 3;
                sender.multiPartParams = {
                    Bucket: sender.bucket,
                    Key: sender.subfolder + "/" + sender.fileKey,
                    ContentType: file.type
                };
                var multipartMap = {
                    Parts: []
                };

                console.log("Creating multipart upload for:", sender.fileKey);
                sender.s3.createMultipartUpload(sender.multiPartParams, function(mpErr, multipart){
                    if (mpErr) { console.log('Error!', mpErr); return; }
                    console.log("Got upload ID", multipart.UploadId);

                    // Grab each partSize chunk and upload it as a part
                    for (var rangeStart = 0; rangeStart < sender.buffer.byteLength; rangeStart += sender.partSize) {
                        sender.partNum++;
                        var end = Math.min(rangeStart + sender.partSize, sender.buffer.byteLength),
                            partParams = {
                              Body: sender.buffer.slice(rangeStart, end),
                              Bucket: sender.bucket,
                              Key: sender.subfolder + "/" + sender.fileKey,
                              PartNumber: String(sender.partNum),
                              UploadId: multipart.UploadId
                            };

                        // Send a single part
                        console.log('Uploading part: #', partParams.PartNumber, ', Range start:', rangeStart);
                        //updateProgress(sender);
                        uploadPart(sender, sender.s3, multipart, partParams);
                    }
                });
            }
        }

        // Handle files of file tag
        var handleFiles = function(files) {
            if (!sender.bucket){
                alert("Select a bucket for uploading");
                return;
            }
            files = [...files]
            initializeProgress(files.length)
            files.forEach(uploadFile)
            files.forEach(previewFile)
        }

        // Handle dropped files
        this.dropArea.addEventListener('drop', function(e){
            if (sender.status) return;
            var dt = e.dataTransfer
            var files = dt.files
            handleFiles(files)
        }, false);

        // add eventlistener when the file tag is changed
        document.querySelector('#' + this.form_id + ' .fileElem').addEventListener('change', function(e){
            var files = e.target.files;
            handleFiles(files)
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
    set_bucket(bucket){
        console.log(this.bucket);
        this.bucket = bucket;
        console.log(this.bucket);
        console.log("--------------------------");
    }
}