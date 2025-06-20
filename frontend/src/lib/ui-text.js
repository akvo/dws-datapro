import React, { Fragment } from "react";

const uiText = {
  en: {
    // Sidebar Menu Labels
    menuUsers: "Users",
    menuControlCenter: "Control Center",
    menuManagePlatformUsers: "Manage Platform Users",
    menuValidationTree: "Validation Tree",
    menuManageMobileUsers: "Manage Mobile Users",
    menuManageRoles: "Manage Roles",
    menuMasterData: "Master Data",
    menuAdministrativeList: "Administrative List",
    menuAttributes: "Attributes",
    menuEntities: "Entities",
    menuEntityTypes: "Entity Types",
    menuOrganisations: "Organisations",
    menuData: "Data",
    menuManageData: "Manage Data",
    menuPendingSubmissions: "Submissions",
    menuApprovals: "Approvals",
    menuDownloads: "Downloads",

    // Login
    loginLoadingTex: (
      <Fragment>
        Verifying
        <br />
        <small>Please wait..</small>
      </Fragment>
    ),
    // Error messages
    error: "Error",
    errorPageNA: "Oops, this page is not available",
    errorAuth: "You are not authorised to access this page",
    errorUnknown: "An unknown error occurred",
    errorURL: (
      <Fragment>
        Please check the URL again or let us take you back to the{" "}
        {window.appConfig.name} homepage
      </Fragment>
    ),
    errorVerifyCreds:
      "Please verify your credentials for the requested resource",
    backHome: "Back to Homepage",
    errorDataLoad: "Could not load data",
    errorUserLoad: "Failed to load user data",
    errorFileList: "Could not fetch File list",
    errorSomething: "Something went wrong",
    errorMandatoryFields: "Please answer all the mandatory questions",
    errorFileUpload: "Could not upload file",
    // Header Links
    controlCenter: "Control Center",
    myProfile: "My Profile",
    settings: "System Settings",
    signOut: "Sign Out",
    dashboards: "Dashboards",
    reports: "Reports",
    newsEvents: "News & Events",
    login: "Log in",
    // Reports
    noTemplate: "No templates found",
    chooseTemplate: "Choose a template",
    backBtn: "Back",
    printBtn: "Print",
    //Events
    upcomingEventText: "Upcoming Events",
    eventTitle: "News & Events",
    latestUpdateText: "Latest Updates",
    // Placeholder text
    lorem:
      "Lorem ipsum dolor sit amet consectetur adipisicing elit. Possimus, assumenda quos? Quia deleniti sapiente aut! Ab consequatur cumque fugit ea. Dolore ex rerum quisquam inventore eum dicta doloribus harum cum.",
    lorem2: "Lorem ipsum dolor sit amet consectetur adipisicing elit.",
    // Charts
    showEmpty: "Show empty values",
    // User Management
    manageDataValidationSetup: "Validation Tree",
    manageUsers: "Manage Users",
    addUser: "Add User",
    addNewUser: "Add new user",
    editUser: "Edit User",
    updateUser: "Update User",
    // Organisation Management
    manageOrganisations: "Manage Organizations",
    addOrganisation: "Add Organization",
    editOrganisation: "Edit Organization",
    updateOrganisation: "Update Organization",
    // Validations
    valFirstName: "First name is required",
    valLastName: "Last name is required",
    valEmail: "Please enter a valid Email Address",
    valPhone: "Phone number is required",
    valRole: "Please select a Role",
    valOrganization: "Please select an Organization",
    valOrgName: "Organization name is required",
    valOrgAttributes: "Please select an Attributes",
    // Control Center
    manageDataTitle: "Manage Data",
    manageDataButton: "Manage Data",
    newSubmissionBtn: "Add New Submission",
    finishSubmissionBtn: "Finish and Go to Manage Data",
    finishSubmissionBatchBtn: "Finish and Go to Batch",
    noFormText: "No data",
    noFormSelectedText: "No form selected",
    manageDataText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Add new data using webforms</li>
          <li>Bulk upload data using spreadsheets</li>
          <li>Download data</li>
        </ul>
      </Fragment>
    ),
    dataDownloadTitle: "Data Download",
    dataDownloadButton: "Download Data",
    dataDownloadText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Access downloaded data</li>
        </ul>
      </Fragment>
    ),
    dataUploadTitle: "Data Upload",
    AdministrationDataUpload: "Administration Data Upload",
    dataUploadButton: "Data Upload",
    dataUploadText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Download upload template</li>
          <li>Bulk upload new data</li>
          <li>Bulk update existing data</li>
        </ul>
      </Fragment>
    ),
    dataAdministrationUploadText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Bulk upload administration data</li>
        </ul>
      </Fragment>
    ),
    AdministrationDataDownload: "Administration Data Download",
    AdministrationDownloadPageHint:
      "Uncheck Prefilled if you only want an upload template",
    dataAdministrationDownloadText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Download administration data</li>
        </ul>
      </Fragment>
    ),
    EntitiesDataUpload: "Entities Data Upload",
    dataEntitiesUploadText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Bulk upload entities data</li>
        </ul>
      </Fragment>
    ),
    EntitiesDataDownload: "Entities Data Download",
    EntitiesDownloadPageHint:
      "Uncheck Prefilled if you only want an upload template",
    dataEntitiesDownloadText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Download entities data</li>
        </ul>
      </Fragment>
    ),
    manageUserTitle: "User Management",
    manageUserButton: "Manage Users",
    manageUserText: (
      <Fragment>
        This is where you manage users based on their roles , regions and
        questionnaire access . You can :
        <ul>
          <li>Add new user</li>
          <li>Modify existing user</li>
          <li>Delete existing user</li>
        </ul>
      </Fragment>
    ),
    manageAttributeText: (
      <Fragment>
        This is where you manage attributes based on their fields. You can :
        <ul>
          <li>Add new attribute</li>
          <li>Modify existing attribute</li>
          <li>Delete existing attribute</li>
        </ul>
      </Fragment>
    ),
    manageEntitiesText: (
      <Fragment>
        This is where you manage entitys based on their fields. You can :
        <ul>
          <li>Add new entity</li>
          <li>Modify existing entity</li>
          <li>Delete existing entity</li>
        </ul>
      </Fragment>
    ),
    manageEntityTypesText: (
      <Fragment>
        This is where you manage entity types based on their fields. You can :
        <ul>
          <li>Add new entity type</li>
          <li>Modify existing entity type</li>
          <li>Delete existing entity type</li>
        </ul>
      </Fragment>
    ),
    manageAdministrativeList: "Manage Administrative List",
    editAdministration: "Edit Administration",
    addAdministration: "Add Administration",
    manageAttributes: "Manage Attributes",
    editAttributes: "Edit Attribute",
    addAttributes: "Add Attribute",
    manageEntities: "Manage Entities",
    manageEntityTypes: "Manage Entity Types",
    addEntities: "Add Entities",
    entityTabTitle: "Entities",
    entityLabel: "Entity",
    exportEntityError: "Unable to export entities",
    administrationLabel: "Administration",
    codeLabel: "Code",
    nameLabel: "Name",
    levelLabel: "Level",
    roleLabel: "Role",
    profileLabel: "Profile",
    profileDes:
      "This page shows your current user setup. It also shows the most important activities for your current user setup",
    ccDescriptionPanel:
      "Instant access to all the administration pages and overview panels for data approvals.",
    // Settings
    orgTabTitle: "Organisations",
    orgPanelTitle: "Manage Organization",
    orgPanelButton: "Manage Organization",
    orgPanelText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Add new organization</li>
          <li>Modify existing organization</li>
          <li>Delete existing organization</li>
        </ul>
      </Fragment>
    ),
    admPanelText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Add new administration</li>
          <li>Modify existing administration</li>
          <li>Delete existing administration</li>
          <li>Bulk upload administration</li>
        </ul>
      </Fragment>
    ),
    settingsDescriptionPanel:
      "This page allows Super Admin to maintain system critical master lists.",
    // Approvals
    approvalsTab1: "My Pending",
    approvalsTab2: "Subordinates Approvals",
    approvalsTab3: "Approved",
    approvalsTitle: "Approvals",
    // Approvers Tree
    notAssigned: "Not assigned",
    questionnaireText: "Questionnaire",
    approversDescription: (
      <Fragment>
        This is where you can see the approvers for each submitted form across
        different administrative areas:
      </Fragment>
    ),
    // Misc
    informUser: "Inform User for Changes",
    // Data Uploads
    batchSelectedDatasets: "Batch Selected Datasets",
    batchDatasets: "Batch Datasets",
    uploadsTab1: "Pending Submission",
    uploadsTab2: "Pending Approval",
    uploadsTab3: "Approved",
    batchName: "Batch Name",
    submissionComment: "Submission comment",
    sendNewRequest: "Notify Approver",
    createNewBatch: "Create a new batch",
    batchHintText: "You are about to create a Batch CSV File",
    batchHintDesc:
      "The operation of merging datasets cannot be undone, and will Create a new batch that will require approval from you admin",
    // Upload Detail
    uploadTab1: "Data Summary",
    uploadTab2: "Raw Data",
    notesFeedback: "Notes & Feedback",
    // Export Data
    generating: "Generating",
    failed: "Failed",
    download: "Download",
    uploadDataLabel: "Upload your data",
    uploadMasterDataLabel: "Upload your data",
    uploadAnotherFileLabel: "Upload Another File",
    backToCenterLabel: "Back to Control Center",
    backToAdmLabel: "Back to Administrative List",
    uploadThankyouText: (
      <Fragment>
        Thank you for uploading the data file. Do note that the data will be
        validated by the system . You will be notified via email if the data
        fails the validation tests . There will also be an attachment of the
        validation errors that needs to be corrected. If there are no validation
        errors , then the data will be forwarded for verification, approval, and
        certification
      </Fragment>
    ),
    exportPanelText: (
      <Fragment>
        <p>
          This page shows your list of data export requests.
          <br />
          For exports which are already generated, please click on the Download
          button to download the data.
        </p>
      </Fragment>
    ),
    // Webform
    formDescription: (
      <p>
        Please fill up the webform below with relevant responses. You will need
        to answer all mandatory questions before you can submit.
        <br />
        Once you have sumitted a webform, please do not forget to add it as part
        of a batch and send it for approval.
      </p>
    ),
    formSuccessTitle: "Thank you for the submission",
    administrationUploadSuccessTitle:
      "Administration Data has been Successfully Uploaded",
    entitiesUploadSuccessTitle: "Entities Data has been Successfully Uploaded",
    formSuccessSubTitle:
      "Do note that this data has NOT been sent for approval. If you are ready to send the submissions for approval, please create a batch and send to the approver",
    formSuccessSubTitleForAdmin:
      "Do note that the data submitted by SUPER ADMIN role will not go through the approval flow and recorded as approved data",
    fetchingForm: "Fetching form..",
    // Forgot Password
    forgotTitle: "Reset your password",
    resetText: "Reset",
    forgotDesc:
      "Enter the email associated with your account and we&apos;ll Send an email with instructions to reset your password",
    instructionsMailed: "Instructions mailed successfully",
    sendInstructions: "Send Instructions",
    // Reset Password
    welcomeShort: (
      <Fragment>
        Welcome to the <b>{window.appConfig.name}</b> platform
      </Fragment>
    ),
    resetHint: (
      <Fragment>
        Please set your password for the platform.
        <br />
        Your password must include:
      </Fragment>
    ),
    invalidInviteTitle: "Invalid Invite Code",
    invalidInviteDesc:
      "Lorem, ipsum dolor sit amet consectetur adipisicing elit. Autem provident voluptatum cum numquam, quidem vitae, qui quam beatae exercitationem ullam perferendis! Nobis in aut fuga voluptate harum, tempore distinctio optio.",
    // Register
    passwordRule1: "Lowercase Character",
    passwordRule2: "Numbers",
    passwordRule3: "Special Character ( -._!`'#%&,:;<>=@{}~$()*+/?[]^|] )",
    passwordRule4: "Uppercase Character",
    passwordRule5: "No White Space",
    passwordRule6: "Minimum 8 Characters",
    passwordUpdateSuccess: "Password updated successfully",
    passwordRequired: "Please input your Password!",
    passwordCriteriaError: "False Password Criteria",
    passwordMatchError: "The two passwords that you entered do not match!",
    accountDisclaimer:
      "The user is accountable for his/her account and in case there are any changes (Transfers, retirement, any kind of leave, resignation etc) this should be communicated to the County Administrator or National Super Admin who might be able to assign the roles to the new officer.",
    // Log in
    loginTitle: "Welcome back",
    contactAdmin: "Please contact the administrator",
    formAssignmentError:
      "You don't have any form assignment, please contact the administrator",
    usernameRequired: "Please input your Username!",
    // Approvals Panel
    panelApprovalsDesc: (
      <Fragment>
        This is where you :
        <ul>
          <li>View pending data approvals awaiting your approval </li>
          <li>View pending approvals by your subordinate approvers</li>
          <li>Assign subordinate approvers</li>
        </ul>
      </Fragment>
    ),
    // Upload Data
    dataExportSuccess: "Data downloaded successfully",
    dataExportFail: "Data download failed",
    fileUploadSuccess: "File uploaded successfully",
    fileUploadFail: "Could not upload file",
    templateFetchFail: "Could not fetch template",
    updateExisting: "Update Existing Data",
    templateDownloadHint:
      "If you do not already have a template, please download",
    templateDownloadAdministrationHint:
      "If you do not already have a template, please ",
    templateDownloadEntityHint:
      "If you do not already have an entity template, please ",
    downloadHere: "download here",
    uploading: "Uploading..",
    dropFile: "Drop your file here",
    selectForm: "Please select a form",
    browseComputer: "Browse your computer",
    usersLoadFail: "Could not load users",
    userDeleteFail: "Could not delete user",
    deleteUserHint:
      "Deleting this user will not delete the data association(s)",
    deleteUserTitle: "You are about to delete the user",
    deleteUserDesc: (
      <Fragment>
        The User will no longer be able to access the {window.appConfig.name}{" "}
        platform as an Enumrator/Admin etc
      </Fragment>
    ),
    userAssociations: "This user has following data association(s)",
    organisationsLoadFail: "Could not load organizations",
    organisationDeleteFail: "Could not delete organization",
    deleteOrganisationDesc: ({ count = 0 }) => (
      <span>
        There are <b>{count} Users</b> associated with this organisation. Please
        reassign or delete these user(s) before deleting the organisation to
        prevent unexpected results
      </span>
    ),
    deleteOrganisationTitle: "You are about to delete the organization",
    // Tour
    prev: "Prev",
    next: "Next",
    finish: "Finish",
    tourControlCenter:
      "Lorem ipsum dolor sit, amet consectetur adipisicing elit",
    tourDataUploads: "Velit amet omnis dolores. Ad eveniet ex beatae dolorum",
    tourApprovals: "Placeat impedit iure quaerat neque sit quasi",
    tourApprovers: "Magni provident aliquam harum cupiditate iste",
    tourManageData: "Lorem ipsum dolor sit, amet consectetur adipisicing elit",
    tourExports: "Velit amet omnis dolores. Ad eveniet ex beatae dolorum",
    tourUserManagement: "Magni provident aliquam harum cupiditate iste",
    tourDataUploadsPanel:
      "Velit amet omnis dolores. Ad eveniet ex beatae dolorum",
    //downloads
    downloadTitle: "Downloads",
    // Add user modal notification
    existingApproverTitle: "There are existing approvers for:",
    existingApproverDescription:
      "Please update the setup in manage validation tree or remove these forms for the current user",
    bulkUploadNoApproverMessage:
      "Can't upload data, because there's no approver yet.",
    batchNoApproverMessage:
      "Can't create batch data, because there's no approver yet.",
    mobilePanelTitle: "Mobile Data Collectors",
    mobilePanelButton: "Manage Data Collectors",
    mobilePanelText: (
      <Fragment>
        This is where you :
        <ul>
          <li>Add new mobile data collector</li>
          <li>Modify existing mobile data collector</li>
          <li>Delete existing mobile data collector</li>
        </ul>
      </Fragment>
    ),
    mobileEditText: "Edit Assignment",
    mobileAddText: "Add Assignment",
    mobileButtonSave: "Save",
    mobileButtonAdd: "Add new data collector",
    mobileLabelName: "Name",
    mobileLabelAdm: "Administrations",
    mobileLabelForms: "Forms",
    mobileNameRequired: "Name is required",
    mobileLevelRequired: "Level is required",
    mobileAdmRequired: "Administration is required: one or multiple",
    mobileFormsRequired: "Form is required: one or multiple",
    mobileSelectAdm: "Select administrations...",
    mobileSelectForms: "Select forms...",
    mobileConfirmDeletion: "Are you sure?",
    mobilePanelAddDesc: (
      <Fragment>
        This page allows you to add mobile data collectors to the{" "}
        {window.appConfig.name} platform.
      </Fragment>
    ),
    mobilePanelEditDesc: (
      <Fragment>
        This page allows you to edit mobile data collectors to the{" "}
        {window.appConfig.name} platform.
      </Fragment>
    ),
    mobileErrDelete: "Unable to delete assingment",
    mobileConfirmDelete: "Are you sure you want to delete this assignment?",
    mobileSuccessAdded: "Mobile assignment added",
    mobileSuccessUpdated: "Mobile assignment update",
    mdPanelTitle: "Master Data",
    mdPanelButton: "Master Data",
    mdPanelText: (
      <Fragment>
        This is where you :
        <ul>
          <li>View all master data</li>
          <li>Modify existing data</li>
          <li>Delete existing data</li>
        </ul>
      </Fragment>
    ),
    formPasscode: "Form Passcode",
    actionColumn: "Action",
    formColumn: "Form",
    nameField: "Name",
    codeField: "Code",
    levelField: "Level",
    administrationField: "Administration",
    nameFieldRequired: "Name is required",
    codeFieldRequired: "Code is required",
    levelFieldRequired: "Level is required",
    admFieldRequired: "Administration is required",
    editButton: "Edit",
    saveButton: "Save",
    saveEditButton: "Save Edits",
    exportButton: "Export",
    bulkUploadButton: "Bulk Upload",
    addNewButton: "Add New",
    cancelButton: "Cancel",
    deleteText: "Delete",
    errDeleteCascadeText1:
      "It is associated with other resources or has cascade restrictions.",
    errDeleteCascadeText2:
      "Please review and resolve dependencies before attempting to delete.",
    manageEntityTitle: "Manage Entities",
    addEntity: "Add New",
    editEntity: "Edit Entity",
    confirmDeleteEntity: "Are you sure you want to delete this entity?",
    errDeleteEntityTitle: "Unable to delete the entity",
    successAddedEntity: "Entity added",
    successUpdatedEntity: "Entity updated",
    successDeletedEntity: "Entity deleted",
    entityText: "Entity",
    entityDataTitle: "Entity Data",
    addEntityData: "Add New",
    editEntityData: "Edit data",
    selectEntity: "Select entity...",
    entityIsRequired: "Entity is required",
    selectLevel: "Select level...",
    selectType: "Select type...",
    selectText: "Select...",
    selectOne: "Select one...",
    confirmDeleteEntityData: "Are you sure you want to delete this data?",
    errDeleteEntityDataTitle: "Unable to delete the data",
    successEntityDataAdded: "Entity data added",
    successEntityDataUpdated: "Entity data updated",
    successEntityDataDeleted: "Entity data deleted",
    entityTypes: "Entity Types",
    entityType: "Entity Type",
    searchEntityType: "Enter name...",
    searchEntity: "Enter name...",
    addOrgDesc: (
      <Fragment>
        This page allows you to add organisations to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    addEntityDesc: (
      <Fragment>
        This page allows you to add entity to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    addEntityTypeDesc: (
      <Fragment>
        This page allows you to add entity type to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    addAttributeDesc: (
      <Fragment>
        This page allows you to add attribute to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    addAdmDesc: (
      <Fragment>
        This page allows you to add administration to the{" "}
        {window.appConfig.name} platform.
      </Fragment>
    ),
    editOrgDesc: (
      <Fragment>
        This page allows you to edit organisations to the{" "}
        {window.appConfig.name} platform.
      </Fragment>
    ),
    editEntityDesc: (
      <Fragment>
        This page allows you to edit entity to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    editEntityTypeDesc: (
      <Fragment>
        This page allows you to edit entity type to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    editAttributeDesc: (
      <Fragment>
        This page allows you to edit attribute to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    editAdmDesc: (
      <Fragment>
        This page allows you to edit administration to the{" "}
        {window.appConfig.name} platform.
      </Fragment>
    ),
    successAddedOrg: "Organisation added",
    successUpdatedOrg: "Organisation updated",
    successDeletedOrg: "Organisation deleted",
    errAddOrg: "Organization could not be added",
    errUpdateOrg: "Organization could not be updated",
    orgLabelName: "Organization Name",
    orgLabelAttr: "Organization Attributes",
    selectAttributes: "Select attributes...",
    admSuccessDeleted: "Administration deleted",
    admSuccessUpdated: "Administration updated",
    admSuccessAdded: "Administration added",
    admErrDeleteTitle: "Unable to delete the administration",
    admConfirmDelete: "Are you sure you want to delete this administration?",
    admParent: "Administration Parent",
    admName: "Administration Name",
    admLevel: "Administration Level",
    admNameRequired: "Administration name is required",
    admTabTitle: "Administrative List",
    attrSuccessDeleted: "Attribute deleted",
    attrSuccessUpdated: "Attribute updated",
    attrSuccessAdded: "Attribute added",
    attrErrDeleteTitle: "Unable to delete the attribute",
    attrConfirmDelete: "Are you sure you want to delete this attribute?",
    attrType: "Attribute type",
    attrName: "Attribute name",
    attrTypeRequired: "Attribute type is required",
    attrNameRequired: "Attribute name is required",
    attrTabTitle: "Attributes",
    addOptionButton: "Add option",
    optionsField: "Options",
    searchNameOrCode: "Enter name or code...",
    userFirstName: "First name",
    userLastName: "Last name",
    userEmail: "Email Address",
    userPhoneNumber: "Phone Number",
    userOrganisation: "Organization",
    userTrained: "Trained",
    userSelectLevelRequired: "Please select an administration level",
    userNationalApprover: "National Approver",
    loadingText: "Loading...",
    questionnairesLabel: "Questionnaires",
    questionnairesRequired:
      "Please select at least one questionnaire access level: Read-only, Editor, or Approver.",
    lastLoginLabel: "Last login",
    submissionsText: "Submissions",
    notifyError: "An error occured",
    successDataUpdated: "Data updated",
    loadMoreLable: "Load More",
    endOfListLabel: "End of List",
    searchPlaceholder: "Search...",
    bulkUploadAttr: "Attributes",
    bulkUploadAttrPlaceholder: "Select Attributes...",
    bulkUploadCheckboxPrefilled: "Prefilled administrative list",
    prefilledAdmModalTitle: "Prefilled Administration requested",
    prefilledAdmModalContent:
      "We're processing your request. Once complete, the prefilled administration template will be sent to your email shortly.  Please keep a close eye on your email, Thank you. ",
    prefilledAdmUploadLabel: "Upload the data",
    prefilledDownloadTitle: "Administrative Download",
    prefilledPanelText: (
      <Fragment>
        <p>
          This page shows your pre-filled administrative data export requests.
          <br />
          For exports which are already generated, please click on the Download
          button to download the data.
        </p>
      </Fragment>
    ),
    errorEntityData: (entity) =>
      `The selected administration doesn't have ${entity} entities`,
    errorEntityNotExists: (entity) =>
      `Unfortunately, ${entity} entities are not yet available. Please get in touch with Admin to add it`,
    questionCol: "Question",
    responseCol: "Response",
    lastResponseCol: "Last Response",
    backManageData: "Back to Manage Data",
    monitoringDataTitle: "Monitoring data",
    monitoringDataDescription: (
      <Fragment>
        This is where you :
        <ul>
          <li>
            Get the list of forms that were collected for this datapoint (new
            and update)
          </li>
          <li>Edit monitoring data</li>
        </ul>
      </Fragment>
    ),
    updateDataButton: "Update data",
    updateDataError: "Unable to update data",
    requiredError: "{{field}} is required",
    helloText: "Hello",
    // User Management
    addUserDescription: (
      <Fragment>
        This page allows you to add users to the {window.appConfig.name}{" "}
        platform. You will only be able to add users for regions under your
        jurisdisction.
        <br />
        Once you have added the user, the user will be notified by email to set
        their password and access the platform
      </Fragment>
    ),
    // Home Page
    homeQuickLinks: [
      { text: "Privacy Policy", href: "/privacy-policy" },
      { text: "Terms & Conditions", href: "/terms-n-conditions" },
      { text: "Cookie Policy", href: "/cookie-policy" },
    ],
    homeJumbotronTitle: <Fragment>{window.appConfig.name}</Fragment>,
    homeJumbotronSubtitle: (
      <Fragment>
        The Fiji {window.appConfig.name} is a comprehensive platform designed to
        enhance the management of water and sewerage services in Fiji.
      </Fragment>
    ),
    homeJumbotronImage: {
      src: "https://images.unsplash.com/photo-1642450909999-7106494ef779?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      alt: "Water landscape",
    },
    homeMandateTitle: "Our Mandate",
    homeMandateText:
      "The Department of Water and Sewerage is mandated with the responsibility of ensuring a sustainable water and sewerage sector through the development of innovative policies, efficient service delivery, and rigorous compliance monitoring.",
    homeStructureTitle: "Department Structure",
    homeStructureText:
      "The Department is headed by the Director of Water and Sewerage with the Technical Unit responsible for monitoring and compliance and Policy Unit responsible for policy and regulatory matters, supported by common cadre support staff.",
    homeStructureImage: {
      src: "https://images.unsplash.com/photo-1744157801849-5e090acbdf84?q=80&w=2089&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      alt: "Water resources",
    },
    homeKeyRolesTitle: "Key Roles and Responsibilities",
    homeKeyRolesText:
      "The key roles and responsibilities of the Department include policy and legislation development, technical and policy advisory, compliance monitoring, and Water Authority of Fiji oversight.",
    homeKeyRolesItems: [
      {
        imgSrc:
          "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        imgAlt: "Water policy",
        title: "Policy & Legislation",
        text: "Formulating regulatory frameworks and policies to promote a sustainable water and sewerage sector. Providing expert advice on water and sewerage issues to support effective governance.",
        type: "right",
      },
      {
        imgSrc:
          "https://images.unsplash.com/photo-1708807472445-d33589e6b090?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        imgAlt: "Compliance monitoring",
        title: "Monitoring & Oversight",
        text: "Overseeing adherence to established policies, legislation, and industry standards. Serving as the primary government agency responsible for monitoring the activities of the Water Authority of Fiji.",
        type: "left",
      },
      {
        imgSrc: "/assets/technical-advisory.jpg",
        imgAlt: "Technical and policy advisory",
        title: "Technical and Policy Advisory",
        text: "Providing expert advice on water and sewerage issues to support effective governance and operational efficiency.",
        type: "right",
      },
      {
        imgSrc:
          "https://plus.unsplash.com/premium_photo-1661964131234-fda88ca041c5?q=80&w=2071&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        imgAlt: "Compliance monitoring",
        title: "Water Authority of Fiji Oversight",
        text: "Serving as the primary government agency responsible for monitoring the activities of the Water Authority of Fiji and ensuring compliance with national regulations.",
        type: "left",
      },
    ],
    homeFooterQuickLinksTitle: "Quick Links",
    homeFooterContactTitle: "Contact Us",
    homeFooterContactDetails: [
      "Department of Water and Sewerage",
      "Ministry of Public Works and Meteorological Services, and Transport",
    ],
    homeFooterContactAddress: [
      "Private Mail Bag, Suva, Fiji",
      "Level 4, Nasilivata House, Ratu Mara Road,",
      "Samabula, Suva",
    ],
    homeFooterContactPhone: "(+679) 3384111",
    homeFooterAboutTitle: <Fragment>About {window.appConfig.name}</Fragment>,
    homeFooterAboutText: (
      <Fragment>
        The Fiji Integrated Water and Sewerage Information Management System (
        {window.appConfig.name}) is a comprehensive platform designed to enhance
        the management of water and sewerage services in Fiji. It serves as a
        centralized hub for data collection, analysis, and reporting, enabling
        informed decision-making and efficient resource allocation.
      </Fragment>
    ),
    homeFooterCopyrightText: "© 2025 Department of Water and Sewerage",
    homeFooterPoweredByText: "Powered by",
    manageDataTab1: "Registration Data",
    manageDataTab2: "Monitoring Data",
    selectFormPlaceholder: "Select Form",
    lastUpdatedCol: "Last Updated",
    nameCol: "Name",
    channelCol: "Channel",
    userCol: "User",
    mobileAppText: "Mobile App",
    webformText: "Webform",
    manageRoles: "Manage Roles",
    manageRoleText: (
      <Fragment>
        This is where you manage roles based on their fields. You can :
        <ul>
          <li>Add new role</li>
          <li>Modify existing role</li>
          <li>Delete existing role</li>
        </ul>
      </Fragment>
    ),
    manageRolesTitle: "Manage Roles",
    addRole: "Add Role",
    editRole: "Edit Role",
    roleName: "Role Name",
    roleNameRequired: "Role name is required",
    roleDescription: "Role Description",
    roleDescriptionRequired: "Role description is required",
    roleAdmLevel: "Administration Level",
    roleAdmLevelRequired: "Administration level is required",
    roleAdmLevelPlaceholder: "Select administration level...",
    roleAccess: "Role Access",
    roleAccessRequired: "Role access is required",
    roleTotalUsers: "Total Users",
    roleSuccessAdded: "Role added",
    roleSuccessUpdated: "Role updated",
    roleSuccessDeleted: "Role deleted",
    roleErrorAdd: "Role could not be added",
    roleErrorUpdate: "Role could not be updated",
    roleErrDeleteTitle: "Unable to delete the role",
    roleDeleteTitle: "You are about to delete the role",
    roleConfirmDelete: "Are you sure you want to delete {roleName}?",
    addRoleDescription: (
      <Fragment>
        This page allows you to add roles to the {window.appConfig.name}{" "}
        platform.
      </Fragment>
    ),
    selectRole: "Select role...",
    rolesRequired: "Please select at least one role",
    yesText: "Yes",
    noText: "No",
  },

  de: {},
};

export default uiText;
