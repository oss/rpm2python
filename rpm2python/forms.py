from flask.ext.wtf import Form, TextField, SelectField
from flask.ext.wtf import Required

#form data for the dropdown menu and searchbar
class SearchForm(Form):
    function_name = TextField('function_name', validators = [Required()])
    searchby = SelectField('searchby', choices = [
                                            ('name', 'Name'),
                                            ('file', 'File'),
                                            ('provides', 'Provides'),
                                            ('requires', 'Requires'),
                                            ('description', 'Description'),
                                            ('summary', 'Summary')])
