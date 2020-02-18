
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