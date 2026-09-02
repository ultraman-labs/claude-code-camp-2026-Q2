require_relative "helper"

class TestOpenAI < Minitest::Test
  FakeContext = Struct.new(:system, :messages, :tools)

  def context
    FakeContext.new("test system", [], {})
  end

  def test_luna_disables_reasoning_for_chat_completions_tools
    backend = Boukensha::Backends::OpenAI.new(
      api_key: "test-key",
      model: "gpt-5.6-luna"
    )

    payload = backend.to_payload(context)

    assert_equal "none", payload[:reasoning_effort]
  end

  def test_other_models_do_not_override_reasoning_effort
    backend = Boukensha::Backends::OpenAI.new(
      api_key: "test-key",
      model: "gpt-5.4-mini"
    )

    payload = backend.to_payload(context)

    refute payload.key?(:reasoning_effort)
  end

  def test_nil_system_prompt_does_not_create_system_message
    backend = Boukensha::Backends::OpenAI.new(
      api_key: "test-key",
      model: "gpt-5.6-luna"
    )

    messages = backend.to_messages(nil, [])

    refute messages.any? { |message| message[:role] == "system" }
  end

  def test_system_prompt_is_preserved
    backend = Boukensha::Backends::OpenAI.new(
      api_key: "test-key",
      model: "gpt-5.6-luna"
    )

    messages = backend.to_messages("You are Boukensha.", [])

    assert_equal(
      [{ role: "system", content: "You are Boukensha." }],
      messages
    )
  end
end
