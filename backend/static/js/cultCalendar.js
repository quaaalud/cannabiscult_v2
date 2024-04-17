/**
 * CalendarManager manages calendar events using MDB Pro Bootstrap library.
 * It allows for adding, removing, and updating events within an MDB Calendar instance.
 */
export class CalendarManager {
    /**
     * Creates an instance of CalendarManager.
     * @param {string} elementId The ID of the DOM element where the calendar will be initialized.
     */
    constructor(eventsList) {
        this.elementId = 'calendar';
        this.element = document.getElementById(this.elementId);
        if (!this.element) throw new Error('Element not found');
        this.colorPalette = [
            { background: '#BBDEFB', foreground: '#0D47A1' }, // Light Blue and Dark Blue
            { background: '#90A4AE', foreground: '#000000' }, // Medium Blue Gray and Black
            { background: '#B3E5FC', foreground: '#01579B' }, // Lighter Blue and Darker Blue
            { background: '#B2EBF2', foreground: '#006064' }, // Cyan and Deep Teal 
            { background: '#B2DFDB', foreground: '#004D40' }, // Light Teal and Dark Teal
            { background: '#E0F7FA', foreground: '#00695C' }, // Lightest Cyan and Teal
            { background: '#ECEFF1', foreground: '#263238' }, // Lightest Gray and Deep Blue Gray
            { background: '#E0F2F1', foreground: '#004D40' }, // Very Light Teal and Dark Teal
            { background: '#CFD8DC', foreground: '#37474F' }, // Light Blue Gray and Dark Blue Gray
            { background: '#B0BEC5', foreground: '#263238' }  // Blue Gray and Deep Blue Gray
            
        ];
        this.colorIndex = Math.floor(Math.random() * this.colorPalette.length);
        this.eventsList = eventsList; // Store the events list passed to the constructor
        this.events = []; // Initialize the events array
        this.processEvents(); // Use the stored events list
        this.initMDBCalendar();
    }
    /**
     * Initializes the MDB Calendar component.
     */
    initMDBCalendar() {
        const spinner = this.element.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }

        this.calendarInstance = Calendar.getInstance(this.element);
        if (this.events.length > 0) {
            this.calendarInstance.addEvents(this.events);
        }
        this.calendarInstance.refresh();
    }
    /**
     * Creates and adds an event to the calendar and internal events array.
     * @param {Object} event The event object to add. The object should include summary, description, start, end, color, and id.
     */
    createEvent(summary, description, startDate, endDate) {
        const color = this.colorPalette[this.colorIndex];
        // Move to the next color, wrapping around if necessary
        this.colorIndex = (this.colorIndex + 1) % this.colorPalette.length;
        const formattedEvent = {
            summary: summary,
            description: description,
            start: { date: startDate, datetime: startDate + 'T09:00:00' },
            end: { date: endDate, datetime: endDate + 'T09:00:00' },
            color: color,
            id: Math.random().toString(36).substr(2, 9) // Generate a random ID
        };

        this.events.push(formattedEvent);
    }
    processEvents() {
        this.eventsList.forEach(event => {
            this.createEvent(event.summary, event.description, event.start_date, event.end_date);
        });
    }
}
 
