async function loadProfession(prof_id){

    let professions = await fetch(`/get_intersection?id=${prof_id}`, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(data => data.json());

    let body = document.createElement('tbody');

    professions.forEach((profession)=>{
        let tr = document.createElement('tr');

        let code = document.createElement('td');
        code.setAttribute('class','uk-text-nowrap');
        code.innerText=profession.code;
        tr.appendChild(code);

        let link = document.createElement('td');
        link.setAttribute('class','uk-table-link');
        let a = document.createElement('a');
        a.setAttribute('class','uk-link-reset');
        a.href=`/profession?id=${profession.id}`;
        a.innerText=profession.name;
        link.appendChild(a);
        tr.appendChild(link);

        let count = document.createElement('td');
        count.setAttribute('class','uk-text-nowrap');
        count.innerText = profession.count;
        tr.appendChild(count);

        body.appendChild(tr)
    })

    let crossTable = document.getElementById('crossTable');
    crossTable.appendChild(body);

    loadcharts(professions,'Пересечения с другими профессиями', 'Пересечений')
}





async function loadTop(prof_id){

    let top = await fetch(`/get_top?id=${prof_id}`, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(data => data.json());


    function createBody(vacancies) {
        let body = document.createElement('tbody');
        vacancies.forEach((vacancy)=>{
            let tr = document.createElement('tr');

            let code = document.createElement('td');
            code.setAttribute('class','uk-text-nowrap');
            code.innerText=vacancy.probability.toString().slice(0,5);
            tr.appendChild(code);

            let link = document.createElement('td');
            link.setAttribute('class','uk-table-link');
            let a = document.createElement('a');
            a.setAttribute('class','uk-link-reset');
            a.href=`/vacancy?id=${vacancy.id}`;
            a.innerText=vacancy.name;
            link.appendChild(a);
            tr.appendChild(link);

            body.appendChild(tr)
        })
        return body
    }


    let bestTable = document.getElementById('topbest');
    bestTable.appendChild(createBody(top.best));
    let worstTable = document.getElementById('topworst');
    worstTable.appendChild(createBody(top.worst));

}