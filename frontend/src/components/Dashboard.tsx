import React, { useEffect, useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api';
import type { SubmissionDetail, MatchResponse, LeaderboardEntry } from '@/lib/api';

// Submissions Table Component
const SubmissionsTable = () => {
  const [submissions, setSubmissions] = useState<SubmissionDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState<number | null>(null);

  useEffect(() => {
    const fetchSubmissions = async () => {
      try {
        const data = await apiClient.getMySubmissions();
        setSubmissions(data);
      } catch (error) {
        console.error('Failed to fetch submissions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSubmissions();
  }, []);

  const handleVerify = async (submissionId: number) => {
    setVerifying(submissionId);
    try {
      await apiClient.verifySubmission(submissionId, 'verified');
      // Update the submission status in the local state
      setSubmissions(submissions.map(sub => 
        sub.submission_id === submissionId 
          ? { ...sub, status: 'verified' } 
          : sub
      ));
    } catch (error) {
      console.error('Failed to verify submission:', error);
    } finally {
      setVerifying(null);
    }
  };

  if (loading) {
    return <div>Loading submissions...</div>;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>My Submissions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {submissions.map((submission) => (
            <Card key={submission.submission_id} className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="text-sm text-gray-500">
                  #{submission.submission_id} - {new Date(submission.submitted_at).toLocaleDateString()}
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 text-sm rounded-full ${
                    submission.status === 'verified' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {submission.status}
                  </span>
                  {submission.status !== 'verified' && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleVerify(submission.submission_id)}
                      disabled={verifying === submission.submission_id}
                    >
                      {verifying === submission.submission_id ? 'Verifying...' : 'Verify'}
                    </Button>
                  )}
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Prompt</h4>
                  <p className="text-gray-600">{submission.prompt}</p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Response</h4>
                  <p className="text-gray-600">{submission.response}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Review Component
const ReviewSubmissions = () => {
  const [match, setMatch] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNextMatch = async () => {
      try {
        const data = await apiClient.getNextMatch();
        setMatch(data);
      } catch (error) {
        console.error('Failed to fetch next match:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNextMatch();
  }, []);

  const handleVote = async (winnerId: number, loserId: number) => {
    if (!match) return;

    try {
      await apiClient.submitComparison(match.comparison_id, {
        winner_submission_id: winnerId,
        loser_submission_id: loserId,
        winner_team_id: match.submission1.team_id,
        loser_team_id: match.submission2.team_id,
        score_difference: 1, // You might want to make this configurable
      });
      // Fetch next match after voting
      const nextMatch = await apiClient.getNextMatch();
      setMatch(nextMatch);
    } catch (error) {
      console.error('Failed to submit vote:', error);
    }
  };

  if (loading) {
    return <div>Loading next match...</div>;
  }

  if (!match) {
    return <div>No matches available for review.</div>;
  }

  return (
    <div className="grid grid-cols-2 gap-6 h-full">
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle>{match.team1_name}'s Submission</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Prompt</h4>
            <p className="text-gray-600">{match.submission1.prompt}</p>
          </div>
          <div>
            <h4 className="font-medium mb-2">Response</h4>
            <p className="text-gray-600">{match.submission1.response}</p>
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-1">
        <CardHeader>
          <CardTitle>{match.team2_name}'s Submission</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Prompt</h4>
            <p className="text-gray-600">{match.submission2.prompt}</p>
          </div>
          <div>
            <h4 className="font-medium mb-2">Response</h4>
            <p className="text-gray-600">{match.submission2.response}</p>
          </div>
        </CardContent>
      </Card>

      <div className="col-span-2 flex justify-center gap-4">
        <Button 
          size="lg" 
          onClick={() => handleVote(match.submission1.submission_id, match.submission2.submission_id)}
        >
          Vote Left
        </Button>
        <Button 
          size="lg"
          onClick={() => handleVote(match.submission2.submission_id, match.submission1.submission_id)}
        >
          Vote Right
        </Button>
      </div>
    </div>
  );
};

// Leaderboard Component
const Leaderboard = () => {
  const [rankings, setRankings] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const data = await apiClient.getLeaderboard();
        setRankings(data);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (loading) {
    return <div>Loading leaderboard...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tournament Leaderboard</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-muted">
              <tr>
                <th className="px-6 py-3 text-sm font-medium">Rank</th>
                <th className="px-6 py-3 text-sm font-medium">Team</th>
                <th className="px-6 py-3 text-sm font-medium">Score</th>
                <th className="px-6 py-3 text-sm font-medium">W/L</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rankings.map((team) => (
                <tr key={team.team_id} className="hover:bg-muted/50">
                  <td className="px-6 py-4 text-sm font-medium">#{team.rank}</td>
                  <td className="px-6 py-4 text-sm">{team.team_name}</td>
                  <td className="px-6 py-4 text-sm">{team.score}</td>
                  <td className="px-6 py-4 text-sm">
                    {team.wins}/{team.losses}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Dashboard Layout
const Dashboard = () => {
  return (
    <div className="p-6">
      <Tabs defaultValue="submissions" className="space-y-6">
        <TabsList>
          <TabsTrigger value="submissions">My Submissions</TabsTrigger>
          <TabsTrigger value="review">Review</TabsTrigger>
          <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
        </TabsList>

        <TabsContent value="submissions">
          <SubmissionsTable />
        </TabsContent>

        <TabsContent value="review">
          <ReviewSubmissions />
        </TabsContent>

        <TabsContent value="leaderboard">
          <Leaderboard />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard; 