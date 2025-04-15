Feature: PRD Generation
  As a product manager
  I want to generate a PRD document from my input
  So that I can create consistent product requirement documentation

  Scenario: Generate a PRD document with markdown format
    Given the PRD Generator API is running
    When I submit a request to generate a PRD with the following data:
      | title        | Example Product      |
      | input_prompt | A video editing tool |
      | format       | markdown             |
    Then I should receive a successful response with status code 200
    And the response should contain a PRD document in markdown format
    And the PRD document should have the title "Example Product"

  Scenario: Generate a PRD document with JSON format
    Given the PRD Generator API is running
    When I submit a request to generate a PRD with the following data:
      | title        | Example Product      |
      | input_prompt | A video editing tool |
      | format       | json                 |
    Then I should receive a successful response with status code 200
    And the response should contain a PRD document in JSON format
    And the PRD document should have the title "Example Product"

  Scenario: Attempt to generate a PRD with invalid format
    Given the PRD Generator API is running
    When I submit a request to generate a PRD with the following data:
      | title        | Example Product      |
      | input_prompt | A video editing tool |
      | format       | invalid_format       |
    Then I should receive a validation error with status code 422
