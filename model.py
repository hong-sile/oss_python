class Event:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.attendees = []

    def attendees_count(self):
        return len(self.attendees)

    def preview_attendees(self):
        return self.attendees[:3]

    def all_attendees(self):
        return self.attendees

    def check_password(self, password):
        return password == self.password

    def already_attended(self, student_id):
        for attendee in self.attendees:
            if attendee.is_equal(student_id):
                return True
        return False

    def attend(self, attendee):
        self.attendees.append(attendee)

    def is_blank(self):
        return len(self.attendees) == 0


class Attendee:
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id

    def is_equal(self, student_id):
        return self.student_id == student_id
