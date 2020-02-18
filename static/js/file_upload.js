
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


    init: function(form_id){
        this.form_id = form_id;
        this.dropArea = document.getElementById(this.form_id)
        var sender = this;  // this object

        this.uploadProgress = []
        this.progressBar = document.querySelector('#' + this.form_id + ' .progress-bar')

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
        var updateProgress = function(fileNumber, percent) {
            sender.uploadProgress[fileNumber] = percent
            let total = sender.uploadProgress.reduce((tot, curr) => tot + curr, 0) / sender.uploadProgress.length
            console.debug('update', fileNumber, percent, total)
            sender.progressBar.value = total
        };

        // upload file to s3
        var uploadFile = function(file, i) {
            var url = 'https://api.cloudinary.com/v1_1/joezimim007/image/upload'
            var xhr = new XMLHttpRequest()
            var formData = new FormData()
            xhr.open('POST', url, true)
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')

            // Update progress (can be used to show progress indicator)
            xhr.upload.addEventListener("progress", function(e) {
                updateProgress(i, (e.loaded * 100.0 / e.total) || 100)
            })

            xhr.addEventListener('readystatechange', function(e) {
                if (xhr.readyState == 4 && xhr.status == 200) {
                  updateProgress(i, 100) // <- Add this
                }
                else if (xhr.readyState == 4 && xhr.status != 200) {
                  // Error. Inform the user
                }
            })

            formData.append('upload_preset', 'ujpu6gyk')
            formData.append('file', file)
            xhr.send(formData)
        }

        // Handle files of file tag
        var handleFiles = function(files) {
            files = [...files]
            initializeProgress(files.length)
            files.forEach(uploadFile)
            files.forEach(previewFile)
        }

        // Handle dropped files
        this.dropArea.addEventListener('drop', function(e){
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
    }
}





var file, fileKey, buffer, bucket;
var startTime = new Date();
var partNum = 0;
var defaultSize = 1024 * 1024 * 5;
var partSize = defaultSize;
var numPartsLeft;
var maxUploadTries = 3;
var multiPartParams
var multipartMap = {
    Parts: []
};


$(document).ready(function(){
    bucket = "jfourie-test";

    AWS.config.apiVersions = {
        s3: '2006-03-01'
    };

    var s3 = new AWS.S3({
        accessKeyId: 'AKIA2YSWAZCCRK2H3SHJ',
        secretAccessKey: '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'
    });

    function completeMultipartUpload(s3, doneParams) {
        s3.completeMultipartUpload(doneParams, function(err, data) {
            if (err) {
              console.log("An error occurred while completing the multipart upload");
              console.log(err);
            } else {
              var delta = (new Date() - startTime) / 1000;
              alert("Finished loading!");
              console.log('Completed upload in', delta, 'seconds');
              console.log('Final upload data:', data);
            }
        });
    }


    function uploadPart(s3, multipart, partParams, tryNum) {
        var tryNum = tryNum || 1;
        s3.uploadPart(partParams, function(multiErr, mData) {
            if (multiErr){
                console.log('multiErr, upload part error:', multiErr);
                if (tryNum < maxUploadTries) {
                    console.log('Retrying upload of part: #', partParams.PartNumber)
                    uploadPart(s3, multipart, partParams, tryNum + 1);
                } else {
                    console.log('Failed uploading part: #', partParams.PartNumber)
                }
                return;
            }
            multipartMap.Parts[this.request.params.PartNumber - 1] = {
                ETag: mData.ETag,
                PartNumber: Number(this.request.params.PartNumber)
            };
            console.log("Completed part", this.request.params.PartNumber);
            console.log('mData', mData);

            if (--numPartsLeft > 0) return; // complete only when all parts uploaded

            var doneParams = {
                Bucket: bucket,
                Key: fileKey,
                MultipartUpload: multipartMap,
                UploadId: multipart.UploadId
            };

            console.log("Completing upload...");
            completeMultipartUpload(s3, doneParams);
            $("#upload").attr("disabled", false);
        });
    }


    $('#upload').click(function(e){
        $("#upload").attr("disabled", true);
        file = $('#fileElem').prop('files')[0];

        const reader = new FileReader();
        reader.readAsArrayBuffer(file)

        reader.onloadend = function onloadend(){
            console.log('on_loaded');
            buffer = reader.result;
            startTime = new Date();
            partNum = 0;
            fileKey = file.name
            partSize = file.size / 10 > defaultSize ? file.size / 10 : defaultSize;
            numPartsLeft = Math.ceil(file.size / partSize);
            maxUploadTries = 3;
            multiPartParams = {
                Bucket: bucket,
                Key: fileKey,
                ContentType: file.type
            };
            var multipartMap = {
                Parts: []
            };

            console.log("Creating multipart upload for:", fileKey);
            s3.createMultipartUpload(multiPartParams, function(mpErr, multipart){
                if (mpErr) { console.log('Error!', mpErr); return; }
                console.log("Got upload ID", multipart.UploadId);

                // Grab each partSize chunk and upload it as a part
                for (var rangeStart = 0; rangeStart < buffer.byteLength; rangeStart += partSize) {
                    partNum++;
                    var end = Math.min(rangeStart + partSize, buffer.byteLength),
                        partParams = {
                          Body: buffer.slice(rangeStart, end),
                          Bucket: bucket,
                          Key: fileKey,
                          PartNumber: String(partNum),
                          UploadId: multipart.UploadId
                        };

                    // Send a single part
                    console.log('Uploading part: #', partParams.PartNumber, ', Range start:', rangeStart);
                    uploadPart(s3, multipart, partParams);
                }
            });
        }
    })
});