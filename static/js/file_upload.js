
var FileUpload = function(){}

FileUpload.prototype ={
    form_id: null,
    dropArea: null,
    uploadProgress: [],
    progressBar: null,
    obj: null;

    init: function(form_id){
        this.form_id = form_id;
        this.dropArea = document.getElementById(this.form_id)
        var sender = this;
        // Prevent default drag behaviors
        ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.preventDefaults, false)
            document.body.addEventListener(eventName, this.preventDefaults, false)
        })

        // Highlight drop area when item is dragged over it
        ;['dragenter', 'dragover'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.highlight, false)
        })

        ;['dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.unhighlight, false)
        })

        this.dropArea.addEventListener('click', this.openDialog, false);


        // Handle dropped files
        this.dropArea.addEventListener('drop', function(e){
            var dt = e.dataTransfer
            var files = dt.files
            sender.handleFiles(files)
        }, false);

        document.querySelector('#' + this.form_id + ' .fileElem').addEventListener('change', function(e){
            var files = e.target.files;
            sender.handleFiles(files)
        }, false);

        this.uploadProgress = []
        this.progressBar = document.querySelector('#' + this.form_id + ' .progress-bar')
    },

    preventDefaults (e) {
        e.preventDefault()
        e.stopPropagation()
    },

    openDialog(e){
        $('#' + this.form_id + ' .fileElem').trigger('click');
    },

    highlight(e) {
        this.classList.add('highlight')
    },

    unhighlight(e) {
        this.classList.remove('active')
    },

    initializeProgress(numFiles) {
        this.progressBar.value = 0
        this.uploadProgress = []

        for(let i = numFiles; i > 0; i--) {
            this.uploadProgress.push(0)
        }
        $('#' + this.form_id + " .gallery").html("");
    },

    updateProgress(fileNumber, percent) {
        this.uploadProgress[fileNumber] = percent
        let total = uploadProgress.reduce((tot, curr) => tot + curr, 0) / uploadProgress.length
        console.debug('update', fileNumber, percent, total)
        this.progressBar.value = total
    },

    handleFiles(files) {
        files = [...files]
        this.initializeProgress(files.length)
        files.forEach(this.uploadFile)
        files.forEach(this.previewFile)
    },

    previewFile(file) {
        let reader = new FileReader()
        reader.readAsDataURL(file)

        reader.onloadend = function() {
            let label = document.createElement('lable');
            label.innerText = file.name;
            console.log(document.querySelector('#' + _this.form_id + ' .gallery'));
            document.querySelector('#' + _this.form_id + ' .gallery').appendChild(label)
            //let img = document.createElement('img')
            //img.src = reader.result
            //document.getElementById('gallery').appendChild(img)
        }
    },

    uploadFile(file, i) {
        var url = 'https://api.cloudinary.com/v1_1/joezimim007/image/upload'
        var xhr = new XMLHttpRequest()
        var formData = new FormData()
        xhr.open('POST', url, true)
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')

        // Update progress (can be used to show progress indicator)
        xhr.upload.addEventListener("progress", function(e) {
            this.updateProgress(i, (e.loaded * 100.0 / e.total) || 100)
        })

        xhr.addEventListener('readystatechange', function(e) {
            if (xhr.readyState == 4 && xhr.status == 200) {
              this.updateProgress(i, 100) // <- Add this
            }
            else if (xhr.readyState == 4 && xhr.status != 200) {
              // Error. Inform the user
            }
        })

        formData.append('upload_preset', 'ujpu6gyk')
        formData.append('file', file)
        xhr.send(formData)
    }
}

//class FileUpload {
//    constructor(form_id){
//        this.form_id = form_id;
//        this.init();
//    }
//
//    init(){
//        this.dropArea = document.getElementById(this.form_id)
//
//        // Prevent default drag behaviors
//        ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
//            this.dropArea.addEventListener(eventName, this.preventDefaults, false)
//            document.body.addEventListener(eventName, this.preventDefaults, false)
//        })
//
//        // Highlight drop area when item is dragged over it
//        ;['dragenter', 'dragover'].forEach(eventName => {
//            this.dropArea.addEventListener(eventName, this.highlight, false)
//        })
//
//        ;['dragleave', 'drop'].forEach(eventName => {
//            this.dropArea.addEventListener(eventName, this.unhighlight, false)
//        })
//
//        this.dropArea.addEventListener('click', this.openDialog, false);
//
//        // Handle dropped files
//        this.dropArea.addEventListener('drop', this.handleDrop, false)
//
//        this.uploadProgress = []
//        this.progressBar = document.querySelector('#' + this.form_id + ' .progress-bar')
//    }
//
//    preventDefaults (e) {
//        e.preventDefault()
//        e.stopPropagation()
//    }
//
//    openDialog(e){
//        $('#' + this.form_id + ' .fileElem').trigger('click');
//    }
//
//    highlight(e) {
//        this.dropArea.classList.add('highlight')
//    }
//
//    unhighlight(e) {
//        this.dropArea.classList.remove('active')
//    }
//
//    handleDrop(e){
//        var dt = e.dataTransfer
//        var files = dt.files
//
//        handleFiles(files)
//    }
//
//    initializeProgress(numFiles) {
//        this.progressBar.value = 0
//        this.uploadProgress = []
//
//        for(let i = numFiles; i > 0; i--) {
//            this.uploadProgress.push(0)
//        }
//        document.querySelector('#' + form_id + " .gallery").html("");
//    }
//
//    updateProgress(fileNumber, percent) {
//        this.uploadProgress[fileNumber] = percent
//        let total = uploadProgress.reduce((tot, curr) => tot + curr, 0) / uploadProgress.length
//        console.debug('update', fileNumber, percent, total)
//        this.progressBar.value = total
//    }
//
//    handleFiles(files) {
//        files = [...files]
//        this.initializeProgress(files.length)
//        this.files.forEach(this.uploadFile)
//        this.files.forEach(this.previewFile)
//    }
//
//    previewFile(file) {
//        let reader = new FileReader()
//        reader.readAsDataURL(file)
//        reader.onloadend = function() {
//            let label = document.createElement('lable');
//            label.innerText = file.name;
//            document.querySelector('#' + this.form_id + ' .gallery').appendChild(label)
//            //let img = document.createElement('img')
//            //img.src = reader.result
//            //document.getElementById('gallery').appendChild(img)
//        }
//    }
//
//    uploadFile(file, i) {
//        var url = 'https://api.cloudinary.com/v1_1/joezimim007/image/upload'
//        var xhr = new XMLHttpRequest()
//        var formData = new FormData()
//        xhr.open('POST', url, true)
//        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
//
//        // Update progress (can be used to show progress indicator)
//        xhr.upload.addEventListener("progress", function(e) {
//            this.updateProgress(i, (e.loaded * 100.0 / e.total) || 100)
//        })
//
//        xhr.addEventListener('readystatechange', function(e) {
//            if (xhr.readyState == 4 && xhr.status == 200) {
//              this.updateProgress(i, 100) // <- Add this
//            }
//            else if (xhr.readyState == 4 && xhr.status != 200) {
//              // Error. Inform the user
//            }
//        })
//
//        formData.append('upload_preset', 'ujpu6gyk')
//        formData.append('file', file)
//        xhr.send(formData)
//    }
//}