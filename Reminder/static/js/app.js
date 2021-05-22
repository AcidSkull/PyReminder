let accordion = document.getElementsByClassName("accordion");

for (i = 0; i < accordion.length; i++) {
    accordion[i].addEventListener("click", function() {
        this.classList.toggle("active");
        
        let p = this.nextElementSibling;

        if (p.style.maxHeight) {
            p.style.padding = "0";
            p.style.maxHeight = null;
        } else {
            p.style.padding = "18px";
            p.style.maxHeight = p.scrollHeight + "px";
        } 
  });
}

let p = document.getElementsByClassName('panel');
p[2].style.maxHeight = p[2].scrollHeight + "px";