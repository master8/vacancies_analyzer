function loadcharts(professions, title, label){

    function getRandomColor() {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }


    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: professions.map(obj=>obj.code),
            datasets: [{
                label: label,
                data: professions.map(obj=>obj['count']),
                backgroundColor: professions.map(()=>getRandomColor()),
                borderWidth: 1,
            }]
        },
        options: {
            onClick: function(evt) {

                var activePoints = myChart.getElementsAtEvent(evt);
                var selectedIndex = activePoints[0]._index;
                var name = professions.filter((obj)=>
                            obj.code === this.data.labels[selectedIndex]);

                console.log(name[0]['profstandard_id'])
                console.log(myChart.data.labels[selectedIndex]);
                document.location.href = '/profession?id='+name[0]['profstandard_id'];
            },
            onHover: function(e) {
                 var point = this.getElementAtEvent(e);
                 if (point.length) e.target.style.cursor = 'pointer';
                 else e.target.style.cursor = 'default';
              },
            tooltips:{
                callbacks: {
                    title: ((tooltipItems, data) =>{
                        var name = professions.filter((obj)=>
                            obj.code === tooltipItems[0]['label']);

                        return name[0].name
                    })}
            },
            title:{
                display: true,
                text: title,
                fontSize: 18,
                position: 'top'
            },
            legend:{
                display: false,
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                    },
                    gridLines: {
                        lineWidth: 5,
                        drawBorder: false
                    }
                }]
            }
        }
    });

}
