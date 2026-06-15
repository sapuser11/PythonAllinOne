//Provide the complete path to the Master-Data model to access the Employee_Registration entity
//Example - namespace capm.db.md;
using capm.db.md as srv from '../db/Master-Data';

service EmployeeRegistrationService {

    entity Employees as select from srv.Employee_Registration; //This will expose the Employee_Registration entity from the Master-Data model
}