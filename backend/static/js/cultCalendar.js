const events = [
  	{
        summary: 'Cannabis Cult Connoisseur Pack',
        description: 'Connoisseur Packs are Back!',
        start: {
            date: new Date('2024-02-20'),
        },
        end: {
            date: new Date('2024-02-20'),
        },
        color: {
            background: '#cfe0fc',
            foreground: '#0a47a9',
        },
        id: 1
    },
];

const calendarElement = document.getElementById('calendar');
calendarElement.classList.add('calendar');
let newEventId = events.length;

const calendarInstance = new Calendar(calendarElement, {
    newEventAttributes: (event) => {
        newEventId++;

        return {
            ...event,
            id: newEventId
        }
    }
});

calendarInstance.addEvents(events);

calendarElement.addEventListener('addEvent.mdb.calendar', (e) => {
    console.log(e.event);
    console.log(calendarInstance.events);
});
