def test_description_here(self):
        # Arrange
        user_query1 = "First input example"

        expected_output1 = "Expected output for first input"


        # Act
        response1 = getResponseFromLLM(user_query1)


        # Debugging (Optional Prints)
        print(f"Test: {user_query1}")
        print(f"Expected: {expected_output1}")
        print(f"Actual: {response1}")


        # Assert
        self.assertEqual(response1, expected_output1) 
