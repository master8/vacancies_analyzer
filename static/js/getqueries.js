function appendTable(profession){
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

    return tr
}

async function loadProfession(prof_id){

    let professions = await fetch(`/get_intersection?id=${prof_id}`, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(data => data.json())
        .catch(error => window.location.href = '/');

    let body = document.createElement('tbody');

    professions.forEach((profession)=>{
        let tr = appendTable(profession);

        body.appendChild(tr)
    });

    let crossTable = document.getElementById('crossTable');
    crossTable.appendChild(body);

    loadcharts(professions,'Пересечения с другими профессиями', 'Пересечений')
    // скрытие спиннера
    document.getElementById('spinnerTable').setAttribute('style','display:none')
}

async function loadResults(){

    let response = await fetch(`/get_results`, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(data => data.json())
        .catch(error => window.location.href = '/');
    let professions = response['professions'];
    document.getElementById('total').innerText=`Итого: ${response['total']}`;
    let body = document.createElement('tbody');

    professions.forEach((profession)=>{
        let tr = appendTable(profession);

        let freq = document.createElement('td');
        freq.setAttribute('class','uk-text-nowrap');
        freq.innerText = profession.rate;
        tr.appendChild(freq);

        body.appendChild(tr)
    });

    let crossTable = document.getElementById('crossTable');
    crossTable.appendChild(body);

    loadcharts(professions,'Число вакансий', 'Число вакансий')
    // скрытие спиннера
    document.getElementById('spinnerTable').setAttribute('style','display:none')
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
    }).then(data => data.json())
        .catch(error => window.location.href = '/');


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
    // скрытие спиннера
    document.getElementById('spinnerTop').setAttribute('style','display:none')
    document.getElementById('spinnerWorst').setAttribute('style','display:none')

}

function createCheckBox(name,part,ids,selected){
    let newCheckbox = document.createElement("input");
    newCheckbox.setAttribute('class','uk-checkbox mode-view');
    newCheckbox.setAttribute('type','checkbox');
    newCheckbox.setAttribute('style','float: left; margin: 6px');
    newCheckbox.setAttribute('name',name);
    newCheckbox.setAttribute('hidden','');
    newCheckbox.value = part['id'];
    if (selected[ids].includes(part['id']))
        newCheckbox.setAttribute('checked','');
    return newCheckbox
}

function createLinkName(part, classType, totalCount){
    let partLink = document.createElement('a');
    partLink.href='#';
    partLink.setAttribute('class','uk-accordion-title');
    let spanTitle = document.createElement('span');
    spanTitle.innerText=part['weight'] +` (0% из ${(part['count']*100/totalCount).toString().slice(0,5)}%)`;
    spanTitle.setAttribute('class',`uk-label ${classType}`);
    partLink.appendChild(spanTitle);
    partLink.innerHTML+=` ${part['name']}`;
    return partLink
}

function createAccordionMeta(partType, part, depth){
    //              2 элемента добавил, идем вглубь
    //              контент аккордеона, 4 уровень
    let accordionGeneralFunction = document.createElement('div');
    accordionGeneralFunction.setAttribute('class','uk-accordion-content uk-margin-large-left');
    accordionGeneralFunction.setAttribute('aria-hidden','false')
    //                  описание ген функции, 5 уровень
    let articleMeta = document.createElement(depth);
    articleMeta.setAttribute('class','uk-article-meta');
    articleMeta.innerHTML=`${ partType }: ${ part['count']} найдено <br> 
                            Частые слова: ${ part['monogram'].join(', ')  }.<br> 
                            Частые словосочетания: ${ part['bigram'].join(', ')  }`;
    //                  добавление описания на 5 уровень
    accordionGeneralFunction.appendChild(articleMeta);
    //                  Список функций, 5 уровень
    return accordionGeneralFunction
}

async function loadBranch(prof_id){
    let generator = document.getElementById('branchesGenerator');

    let response = await fetch(`/get_branches?id=${prof_id}`, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(data => data.json())
        .catch(error => window.location.href = '/');
    let count = response['count'];
    let topWords = response['topWords'];
    let topBigrams = response['topBigrams'];



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
            branchList.appendChild(li)
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
            let selectBoxGeneral = createCheckBox('gf',general_function,'general_fun_ids',selected);
            li.appendChild(selectBoxGeneral);
            //              ссылка аккордеона, 4 уровень
            let generalTitle = createLinkName(general_function,'uk-label-danger', count);
            li.appendChild(generalTitle);

            let accordionGeneralFunction = createAccordionMeta('Функций', general_function, 'h3');
            li.appendChild(accordionGeneralFunction);

            let ulFunction = document.createElement('ul');
            ulFunction.setAttribute('uk-accordion','');
            ulFunction.setAttribute('class','uk-accordion');

            //                      функции, 6 уровень
            let functions = general_function['functions'];
            functions.forEach(func =>{
                let liFunction = document.createElement('li');
                //                      галочка на функции, 7 уровень
                let selectBoxFunction = createCheckBox('f',func,'fun_ids', selected);
                liFunction.appendChild(selectBoxFunction);
                //                      ссылка на функции, 7 уровень
                let funcTitle = createLinkName(func,'uk-label-success', count)
                liFunction.appendChild(funcTitle);

                let accordionFunction = createAccordionMeta('Характеристик', func,'h4')

                let ulPart = document.createElement('ul');
                ulPart.setAttribute('uk-accordion','');
                ulPart.setAttribute('class','uk-accordion');

                let parts = func['parts'];
                parts.forEach(part =>{
                    let liPart = document.createElement('li');

                    let selectBoxPart = createCheckBox('p',part,'part_ids', selected);
                    liPart.appendChild(selectBoxPart);

                    let partTitle = createLinkName(part,'', count)
                    liPart.appendChild(partTitle);

                    let partFunction = createAccordionMeta('Частей характеристики', part,'h4')
                                        let partTable = document.createElement('table');
                    partTable.setAttribute('class', 'uk-table uk-table-small uk-table-divider');

                    let partTableHead= document.createElement('thead');
                    let partTableBody= document.createElement('tbody');

                    partTableHead.innerHTML=`<tr>                       
                                                <th class="uk-table-shrink">Близость</th>
                                                <th class="uk-table-expand">Часть вакансии</th>
                                            </tr>`;

                    let vacancy_parts = part['vacancy_parts'];
                    vacancy_parts.forEach((vacancy,index) => {
                        if (index>4) return true;
                        let trVacancy = document.createElement('tr');
                        trVacancy.innerHTML=`<td>${ vacancy['similarity'].toString().substring(0,4) }</td>
                                            <td>${ vacancy['vacancy_part'] }</td>`
                        partTableBody.appendChild(trVacancy)
                    })

                    partTable.appendChild(partTableHead);
                    partTable.appendChild(partTableBody);
                    partFunction.appendChild(partTable);

                    liPart.appendChild(partFunction);
                    ulPart.appendChild(liPart);
                });

                accordionFunction.appendChild(ulPart)

                liFunction.appendChild(accordionFunction);
                ulFunction.appendChild(liFunction)
            });

            accordionGeneralFunction.appendChild(ulFunction);
            accordion.appendChild(li)
        });

        secondColumn.appendChild(accordion); // всего 1 элемент

        grid.appendChild(firstColumn);
        grid.appendChild(secondColumn);
        generator.appendChild(grid)
    })



    let countTopWords = document.getElementById('countTopWords');
    countTopWords.setAttribute('class','uk-article-meta');
    countTopWords.innerHTML=`Обобщенных функций: ${ count } найдено <br> 
                               Частые слова: ${ topWords.join(', ') } <br> 
                               Частые словосочетания: ${ topBigrams.join(', ') } `
    // скрытие спиннера
    document.getElementById('spinnerBranch').setAttribute('style','display:none')
}
