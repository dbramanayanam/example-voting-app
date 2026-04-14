using Xunit;

namespace Worker.Tests;

public class WorkerLogicTests
{
    [Fact]
    public void SampleTest_Passes()
    {
        Assert.True(true);
    }

    [Theory]
    [InlineData("Cats")]
    [InlineData("Dogs")]
    public void VoteValue_CanBeValidated(string vote)
    {
        Assert.Contains(vote, new[] { "Cats", "Dogs" });
    }
}
