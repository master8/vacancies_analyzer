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
    });

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
        });
        return body
    }


    let bestTable = document.getElementById('topbest');
    bestTable.appendChild(createBody(top.best));
    let worstTable = document.getElementById('topworst');
    worstTable.appendChild(createBody(top.worst));

}



async function loadBranch(prof_id){

    let response = await fetch(`/get_branches?id=${prof_id}`, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(data => data.json());

    let generator = document.getElementById('brachesGenerator');

    let branches = response['branches'];
    let selected = response['selected'];



    branches.forEach(branch=>{
        // 0 уровень
        let grid = document.createElement('div');
        grid.setAttribute('class', 'uk-grid-divider uk-child-width-expand@s');
        grid.setAttribute('uk-grid',"");
        //      Левая колонка, 1 уровень
        let firstColumn =  document.createElement('div');
        firstColumn.setAttribute('class','uk-width-1-6@m uk-first-column');
        //          Уровень:, 2 уровень
        let level = document.createElement('h4');
        level.innerText = `Уровень: ${branch['level']}`;
        firstColumn.appendChild(level);
        //          Список постов, 2 уровень
        let posts = branch['posts'];
        let branchList = document.createElement('ul');
        branchList.setAttribute('class','uk-list');
        //              Список постов, 3 уровень
        posts.forEach(post=>{
            let li = document.createElement('li');
            li.innerText=post;
            branchList.appendChild(branchList)
        });
        firstColumn.appendChild(branchList); // всего 2 элемента, оба присоединил

        //      Правая колонка, 1 уровень
        let secondColumn = document.createElement('div');
        //          ul внутри, 2 уровень
        let accordion = document.createElement('ul');
        accordion.setAttribute('class','uk-accordion');
        accordion.setAttribute('uk-accordion','');
        //              li обобщенная функция, 3 уровень
        let general_functions = branch['general_functions'];
        general_functions.forEach(general_function=>{
            let li = document.createElement('li');
            li.setAttribute('class','uk-open');
            //              галочка на обобщенной функции, 4 уровень
            let selectBoxGeneral = document.createElement("input");
            selectBoxGeneral.setAttribute('class','uk-checkbox mode-view');
            selectBoxGeneral.setAttribute('type','checkbox');
            selectBoxGeneral.setAttribute('style','float: left; margin: 6px');
            selectBoxGeneral.setAttribute('name','gf');
            selectBoxGeneral.setAttribute('hidden','');
            selectBoxGeneral.value = general_function['id'];
            if (selected['general_fun_ids'].includes(general_function.id))
                //TODO Проверить работоспособность сохранения значения выбранных
                selectBoxGeneral.setAttribute('checked','');
            li.appendChild(selectBoxGeneral)
            //              ссылка аккордеона, 4 уровень
            let generalTitle = document.createElement('a');
            generalTitle.href='#';
            generalTitle.setAttribute('class','uk-accordion-title');
            //                  спан внутри, 5 уровень
            let spanTitle = document.createElement('span');
            spanTitle.innerText=general_function['weight'];
            spanTitle.setAttribute('class','uk-label uk-label-success');
            generalTitle.appendChild(spanTitle);
            //              имя аккордеона, 4 уровень
            spanTitle.innerText=general_function['name'];
            li.appendChild(spanTitle);
            //              2 элемента добавил, идем вглубь
            //              контент аккордеона, 4 уровень
            let accordionGeneralFunction = document.createElement('div');
            accordionGeneralFunction.setAttribute('class','uk-accordion-content uk-margin-large-left');
            accordionGeneralFunction.setAttribute('aria-hidden','false')
            //                  описание ген функции, 5 уровень
            let articleMeta = document.createElement('h3');
            articleMeta.setAttribute('class','uk-article-meta');
            articleMeta.innerHTML=`Характеристик: ${ general_function['count'] } найдено <br> 
                                    Частые слова: ${ general_function['monogram'] }.<br> 
                                    Частые словосочетания: ${ general_function['bigram'] }`;
            accordionGeneralFunction.appendChild(articleMeta);




            li.appendChild(accordionGeneralFunction);
            accordion.appendChild(li)
        })

        secondColumn.appendChild(accordion) // всего 1 элемент

        grid.appendChild(firstColumn)
        grid.appendChild(secondColumn)
        generator.appendChild(grid)
    })




}
